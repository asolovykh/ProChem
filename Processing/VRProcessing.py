import os
import traceback
import numpy as np
import pandas as pd
from Gui.VRProcessingGUI_dev import Ui_VRProcessing, QMainWindow
from Processing.VROszicar import VROszicarProcessing, VRPdModel
from Processing.VRGraph import VRGraph
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QFileDialog, QAbstractItemView
from PySide6.QtGui import QCloseEvent
from Logs.VRLogger import sendDataToLogger


class VRProcessing(Ui_VRProcessing, QMainWindow):
    """VaspReader processing class. Initialising of this class create a window for processing molecular dynamic results
       from VASP program. Use this with mainloop function, which work with events sent by window."""
    calc_const = 2 * 9.65 * 1000
    coordProjection = ('_x', '_y', '_z')
    directProjection = ('_dir_1', '_dir_2', '_dir_3')

    @sendDataToLogger
    def __init__(self, app, settings, visualWindowObject, printWindowObject, openGlWindowObject, calculation, name, deleteAfterLeave):
        super(VRProcessing, self).__init__()
        self.__app = app
        self.__settings = settings
        location = self.__settings.processingWindowLocation
        self.__parent = visualWindowObject
        self.__logger = printWindowObject
        self.__openGl = openGlWindowObject
        self.setupUi(self)
        if location is not None:
            self.move(location[0], location[1])
        self.__calculation = calculation
        self._deleteAfterLeave = deleteAfterLeave
        self._name = name
        self._selected_atoms = self.__calculation['ATOMNAMES']

        self.__graph = None
        self._selected_columns = []
        self._masses = self.selectedDataForm('MASSES')
        self._selectedNames = self.selectedDataForm('ID')

        if self._selectedNames:
            self.columnsNames = self.removeSubscriptInNames(self._selectedNames)
            self.coordColumns = [name + self.coordProjection[j] for name in self.columnsNames for j in range(3)]
            self.directColumns = [name + self.directProjection[j] for name in self.columnsNames for j in range(3)]
            self.baseDf = self.formBasePandasDf()
            self.vColumns, self.eColumns = self.velocitiesAndEnergiesCalc()
            self.distanceCols, self.angleCols, self.weightmassCols, self.sumCols, self.differenceCols, self.divideCols = [], [], [], [], [], []
            self.baseDf.drop(self.baseDf.index[-1], inplace=True)
            self.mainDf = pd.DataFrame(self.baseDf)
            for v in self.vColumns:
                del self.mainDf[v]
            for d in self.directColumns:
                del self.mainDf[d]
            self.coordinatesDelete()
            self.refreshLists()
            self.oszicarCheckboxUnlock()
        else:
            self.mainDf = pd.DataFrame()
            timeArr = np.arange(0, float(self.__calculation['POTIM'][0]) * self.__calculation['STEPS_LIST'][0], float(self.__calculation['POTIM'][0]))
            for index, steps in enumerate(self.__calculation['STEPS_LIST'][1:], start=1):
                addTimeArr = np.arange(timeArr[-1] + float(self.__calculation['POTIM'][index]), timeArr[-1] + float(self.__calculation['POTIM'][index]) * steps, float(self.__calculation['POTIM'][index]))
                timeArr = np.concatenate([timeArr, addTimeArr])
            self.mainDf.insert(0, 'Time, fs', timeArr[:self.__calculation['STEPS']])
        self._model = VRPdModel(self.mainDf)
        self.ViewTable.setModel(self._model)
        self._selectionModel = QItemSelectionModel(self._model)
        self.ViewTable.setSelectionModel(self._selectionModel)
        self.linkElementsWithFunctions()
        self.__parent.hide()
        self.__openGl.hide()

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger
    def linkElementsWithFunctions(self):
        self.DCList.itemClicked.connect(self.DCListAction)
        self.DistanceRadio.toggled.connect(self.DCListClear)
        self.DCAddCol.clicked.connect(self.DCButtonClicked)
        self.DCAdded.activated.connect(self.DCChooseToRemove)
        self.DCRemoveCol.clicked.connect(lambda: self.removeColumns(self.DCAdded, self.DCRemoveCol))
        self.PMList.itemClicked.connect(self.PMListAction)
        self.MinusRadio.toggled.connect(self.PMListClear)
        self.PMAddCol.clicked.connect(self.PMButtonClicked)
        self.PMAdded.activated.connect(self.PMChooseToRemove)
        self.PMRemoveCol.clicked.connect(lambda: self.removeColumns(self.PMAdded, self.PMRemoveCol))
        self.AngleList.itemClicked.connect(self.AngleListAction)
        self.AngleAddCol.clicked.connect(self.AngleButtonClicked)
        self.AngleAdded.activated.connect(self.AngleChooseToRemove)
        self.AngleRemoveCol.clicked.connect(lambda: self.removeColumns(self.AngleAdded, self.AngleRemoveCol))
        self.DivideList.itemClicked.connect(self.DivideListAction)
        self.DivideAddCol.clicked.connect(self.DivideButtonClicked)
        self.DivideAdded.activated.connect(self.DivideChooseToRemove)
        self.DivideRemoveCol.clicked.connect(lambda: self.removeColumns(self.DivideAdded, self.DivideRemoveCol))
        self.AInclude_OSZICAR.toggled.connect(self.oszicarAction)
        self.ADel_coords_of_sel_atoms.toggled.connect(self.delCoordsAction)
        self.ADel_energy_of_sel_atoms.toggled.connect(self.delEnergyAction)
        self.CreateExcel.clicked.connect(self.saveTable)
        self.Back.clicked.connect(self.window().close)
        self.ABack.triggered.connect(self.window().close)
        self.AExit.triggered.connect(lambda: self.closeAll(QCloseEvent()))
        self._selectionModel.selectionChanged.connect(self.columnSelected)
        self.PlotGraphButton.clicked.connect(self.plotGraph)

    @sendDataToLogger
    def closeAll(self, event):
        self.__parent.close()
        event.accept()

    @sendDataToLogger
    def closeEvent(self, event=QCloseEvent()):
        self.__parent.show()
        self.__openGl.show()
        self.__parent.destroyProcessingWindow()
        event.accept()

    @sendDataToLogger
    def refreshLists(self):
        self.DCList.clear()
        self.PMList.clear()
        self.AngleList.clear()
        self.DivideList.clear()
        self.RenameSelect.clear()
        self.DCList.addItems(self.columnsNames)
        self.PMList.addItems(self.mainDf.columns[1:].tolist())
        self.AngleList.addItems(self.columnsNames)
        self.DivideList.addItems(self.columnsNames)
        self.RenameSelect.addItems(self.mainDf.columns[1:].tolist())

    @sendDataToLogger
    def selectedDataForm(self, dict_name):
        return [self.__calculation[dict_name][i] for i in range(self.__calculation['ATOMNUMBER']) if 'Sel' in self._selected_atoms[i]]

    @staticmethod
    def removeSubscriptInNames(names):
        names = names.copy()
        renamed = []
        for name in names:
            renamed.append(''.join(name.split('_')))
        return renamed

    @sendDataToLogger
    def formBasePandasDf(self):
        data = []
        selectedColumnsNums = [num for num, column in enumerate(self._selected_atoms) if 'Sel' in column]
        for step in range(self.__calculation['STEPS']):
            temp, counter = [], 0
            for atom_num in selectedColumnsNums:
                if step > 0:
                    temp.append(self.atomAwayProcessing(self.__calculation['DIRECT'][step][atom_num], data[step - 1][counter]))
                else:
                    temp.append(self.__calculation['DIRECT'][step][atom_num])
                counter += 1
            data.append(temp.copy())
        data = np.asarray(data)
        data = data.reshape((-1, 3 * len(self._selectedNames)))
        baseDf = pd.DataFrame(data, columns=self.directColumns)
        if self._deleteAfterLeave:
            baseDf.mask(baseDf >= 1, inplace=True)
            baseDf.mask(baseDf <= 0, inplace=True)
        timeArr = np.arange(0, float(self.__calculation['POTIM'][0]) * self.__calculation['STEPS_LIST'][0], float(self.__calculation['POTIM'][0]))
        for index, _ in enumerate(self.__calculation['STEPS_LIST'][1:], start=1):
            addTimeArr = np.arange(timeArr[-1] + float(self.__calculation['POTIM'][index]), timeArr[-1] + float(self.__calculation['POTIM'][index]) * (self.__calculation['STEPS_LIST'][index] - self.__calculation['STEPS_LIST'][index - 1] + 1), float(self.__calculation['POTIM'][index]))
            timeArr = np.concatenate([timeArr, addTimeArr])
        baseDf.insert(0, 'Time, fs', timeArr[:self.__calculation['STEPS']])
        for name in self.columnsNames:
            for num, proj in enumerate(self.coordProjection):
               baseDf[f'{name}{proj}'] = self.__calculation['BASIS'][0][num] * baseDf[f'{name}_dir_1'] + self.__calculation['BASIS'][1][num] * baseDf[f'{name}_dir_2'] + self.__calculation['BASIS'][2][num] * baseDf[f'{name}_dir_3']
        return baseDf

    @staticmethod
    def atomAwayProcessing(direct, data):
        column = direct.copy()
        for num, _ in enumerate(direct):
            exprFactor = round(data[num] - direct[num])
            if exprFactor:
                column[num] = column[num] + exprFactor
        return column

    @sendDataToLogger
    def velocitiesAndEnergiesCalc(self):
        vColumns = ['V_' + column for column in self.columnsNames]
        eColumns = ['E_' + column for column in self.columnsNames]
        for num, column in enumerate(vColumns):
            self.baseDf[column] = (self.baseDf[self.columnsNames[num] + '_x'].diff() ** 2 + self.baseDf[self.columnsNames[num] + '_y'].diff() ** 2 + self.baseDf[self.columnsNames[num] + '_z'].diff() ** 2) ** (1 / 2) * 1000
            self.divineOnPOTIM(column)
        for num, column in enumerate(eColumns):
            self.baseDf[column] = (self.baseDf[vColumns[num]]) ** 2 * self._masses[num] / self.calc_const
        self.baseDf.drop(self.baseDf.index[0], inplace=True)
        self.baseDf.reset_index(drop=True, inplace=True)
        return vColumns, eColumns

    @sendDataToLogger
    def coordinatesDelete(self):
        for coord in self.coordColumns:
            del self.mainDf[coord]

    @sendDataToLogger
    def directCurveChoose(self, first, second):
        periodical_coefficients = []
        for proj in ['_dir_1', '_dir_2', '_dir_3']:
            periodical_coefficients.append(round(self.baseDf[second + proj][0] - self.baseDf[first + proj][0]))
        return np.dot(np.asarray(periodical_coefficients), self.__calculation['BASIS'])

    @sendDataToLogger
    def divineOnPOTIM(self, column, isCOM=False):
        prev_index = 0
        for index, POTIM in enumerate(self.__calculation['POTIM']):
            if isCOM:
                if index != len(self.__calculation['POTIM']) - 1:
                    self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index] - 1, column] = self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index] - 1, column] / POTIM
                    prev_index = self.__calculation['STEPS_LIST'][index] - 1
                else:
                    self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index], column] = self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index], column] / POTIM
            else:
                self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index], column] = self.baseDf.loc[prev_index:self.__calculation['STEPS_LIST'][index], column] / POTIM
                prev_index = self.__calculation['STEPS_LIST'][index]

    @sendDataToLogger(operationType='user')
    def removeColumns(self, addedColsElement, removeElement):
        toDelete = addedColsElement.currentText()
        colsList = []
        if addedColsElement == self.DCAdded:
            colsList = self.distanceCols if toDelete in self.distanceCols else self.weightmassCols
        elif addedColsElement == self.PMAdded:
            colsList = self.sumCols if toDelete in self.sumCols else self.differenceCols
        elif addedColsElement == self.AngleAdded:
            colsList = self.angleCols
        elif addedColsElement == self.DivideAdded:
            colsList = self.divideCols

        if colsList == self.distanceCols or colsList == self.angleCols:
            self.baseDf.drop(columns=toDelete, inplace=True)
            self.mainDf.drop(columns=toDelete, inplace=True)
            colsList.remove(toDelete)
            self.addMessage(f'Column {toDelete} has been removed.')
        elif colsList == self.sumCols or colsList == self.differenceCols:
            self.baseDf.drop(columns=toDelete, inplace=True)
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDelete, inplace=True)
            colsList.remove(toDelete)
            self.eColumns.remove(toDelete)
            self.addMessage(f'Column {toDelete} has been removed.')
        elif colsList == self.divideCols:
            elements = toDelete.split('_')
            atoms = []
            for num, element in enumerate(elements):
                if num % 2 == 0:
                    atoms.append(element)
                else:
                    atoms[-1] = atoms[-1] + '_' + element
            toDeleteCols = [f'Evib_{toDelete}', f'Erot_{toDelete}']
            for atom in atoms:
                toDeleteCols.extend([f'Evib_{toDelete}({atom})', f'Erot_{toDelete}({atom})'])
            self.baseDf.drop(columns=toDeleteCols, inplace=True)
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDeleteCols, inplace=True)
            colsList.remove(toDelete)
            [self.eColumns.remove(value) for value in toDeleteCols]
            self.addMessage(f'Columns divided to vibrational and rotational energy {toDelete} have been removed.')
        else:
            toDeleteList = [f'{toDelete}_x', f'{toDelete}_y', f'{toDelete}_z', f'V{toDelete}', f'E{toDelete}']
            self.baseDf.drop(columns=toDeleteList, inplace=True)
            toDeleteList.remove(f'V{toDelete}')
            if not self.ADel_coords_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDeleteList, inplace=True) if not self.ADel_energy_of_sel_atoms.isChecked() else self.mainDf.drop(columns=toDeleteList[:3], inplace=True)
            else:
                if not self.ADel_energy_of_sel_atoms.isChecked():
                    self.mainDf.drop(columns=toDeleteList[-1], inplace=True)
            self.vColumns.remove(f'V{toDelete}')
            self.addMessage(f'Column {self.eColumns[-1]} and linked columns have been removed.')
            self.eColumns.remove(f'E{toDelete}')
            self.columnsNames.remove(toDelete)
            self.weightmassCols.remove(toDelete)
        addedColsElement.removeItem(addedColsElement.currentIndex())
        if not addedColsElement.count():
            addedColsElement.setDisabled(True)
            removeElement.setDisabled(True)
        self.refreshLists()
        self._model.refreshTable(self.mainDf)

    @sendDataToLogger(operationType='user')
    def DCListAction(self, element):
        selectedColumns = self.DCList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 2:
            self.DCAddCol.setEnabled(True)
        elif listSize < 2:
            self.DCAddCol.setDisabled(True)

        if self.DistanceRadio.isChecked():
            if listSize > 2:
                self.DCList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.DCSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    @sendDataToLogger
    def DCListClear(self, *args):
        self.DCSelected.clear()
        self.DCList.clearSelection()
        self.DCAddCol.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def DCButtonClicked(self):
        if self.DistanceRadio.isChecked():
            self.DistanceCalculate()
        else:
            self.COMCalculate()

    @sendDataToLogger
    def DistanceCalculate(self):
        first, second = sorted([item.text() for item in self.DCList.selectedItems()])
        if f'{first}--{second}' in self.baseDf:
            self.addMessage('Column has already been added!', result='FAILED', cause='Column has already been added')
            self.DCListClear()
        else:
            coefficients = self.directCurveChoose(first, second)
            self.baseDf[f'{first}--{second}'] = ((self.baseDf[second + '_x'] - self.baseDf[first + '_x'] - coefficients[0]) ** 2 + (self.baseDf[second + '_y'] - self.baseDf[first + '_y'] - coefficients[1]) ** 2 + (self.baseDf[second + '_z'] - self.baseDf[first + '_z'] - coefficients[2]) ** 2) ** (1 / 2)
            self.mainDf[f'{first}--{second}'] = self.baseDf[f'{first}--{second}']

            self.distanceCols.append(f'{first}--{second}')
            if not self.DCAdded.isEnabled():
                self.DCAdded.setEnabled(True)
            self.DCAdded.addItem(f'{first}--{second}')
            if not self.DCRemoveCol.isEnabled():
                self.DCRemoveCol.setEnabled(True)
            self.refreshLists()
            self.DCListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {first}--{second} has been added.')

    @sendDataToLogger
    def COMCalculate(self, atomsList=None):
        if atomsList is None:
            weightmasses = sorted([item.text() for item in self.DCList.selectedItems()])
        else:
            weightmasses = atomsList
        columnName = 'cm_' + '_'.join(weightmasses)
        if f'E{columnName}' not in self.eColumns:
            weightMassesDict = dict()
            for name in self._selectedNames:
                rname = ''.join(name.split('_'))
                if rname in weightmasses:
                    weightMassesDict[rname] = self.__calculation['MASSES'][self.__calculation['ID-TO-NUM'][name]]
            summaryMass = sum([weightMassesDict[name] for name in weightmasses])
            directCols = ['_dir_1', '_dir_2', '_dir_3']
            for index, proj in enumerate(['_x', '_y', '_z']):
                self.baseDf[f"{columnName}{directCols[index]}"] = np.zeros(self.__calculation['STEPS'] - 2)
                self.baseDf[f"{columnName}{proj}"] = np.zeros(self.__calculation['STEPS'] - 2)
                for atom in weightmasses:
                    self.baseDf[f"{columnName}{proj}"] += self.baseDf[f"{atom}{proj}"] * weightMassesDict[atom] / summaryMass
                    self.baseDf[f"{columnName}{directCols[index]}"] += self.baseDf[f"{atom}{directCols[index]}"] * weightMassesDict[atom] / summaryMass
            self.vColumns.append(f'V{columnName}')
            self.eColumns.append(f'E{columnName}')
            self.baseDf[self.vColumns[-1]] = np.sqrt(self.baseDf[f'{columnName}_x'].diff() ** 2 + self.baseDf[f'{columnName}_y'].diff() ** 2 + self.baseDf[f'{columnName}_z'].diff() ** 2) * 1000
            self.divineOnPOTIM(self.vColumns[-1], True)
            self.baseDf[self.eColumns[-1]] = (self.baseDf[self.vColumns[-1]]) ** 2 * summaryMass / self.calc_const
            if not self.ADel_coords_of_sel_atoms.isChecked():
                self.mainDf.insert(len(self.columnsNames) * 3 + 1, columnName + '_dir_1', self.baseDf[columnName + '_dir_1'])
                self.mainDf.insert(len(self.columnsNames) * 3 + 2, columnName + '_dir_2', self.baseDf[columnName + '_dir_2'])
                self.mainDf.insert(len(self.columnsNames) * 3 + 3, columnName + '_dir_3', self.baseDf[columnName + '_dir_3'])
                self.mainDf.insert(len(self.columnsNames) * 3 + 4, columnName + '_x', self.baseDf[columnName + '_x'])
                self.mainDf.insert(len(self.columnsNames) * 3 + 5, columnName + '_y', self.baseDf[columnName + '_y'])
                self.mainDf.insert(len(self.columnsNames) * 3 + 6, columnName + '_z', self.baseDf[columnName + '_z'])
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.insert(len(self.mainDf.columns), self.eColumns[-1], self.baseDf[self.eColumns[-1]])
            self.columnsNames.append(columnName)
            self.refreshLists()
            self.DCListClear()
            self.weightmassCols.append(columnName)
            self.DCAdded.addItem(columnName)

            if not self.DCAdded.isEnabled():
                self.DCAdded.setEnabled(True)
            if not self.DCRemoveCol.isEnabled():
                self.DCRemoveCol.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {self.eColumns[-1]} has been added.')
        else:
            self.addMessage('Column has already been added!', result='FAILED', cause='Column has already been added')
            self.DCListClear()

    @sendDataToLogger(operationType='user')
    def DCChooseToRemove(self, *args):
        self.DCRemoveCol.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def PMListAction(self, element):
        selectedColumns = self.PMList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 2:
            self.PMAddCol.setEnabled(True)
        elif listSize < 2:
            self.PMAddCol.setDisabled(True)

        if self.MinusRadio.isChecked():
            if listSize > 2:
                self.PMList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.PMSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    @sendDataToLogger
    def PMListClear(self, *args):
        self.PMSelected.clear()
        self.PMList.clearSelection()
        self.PMAddCol.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def PMButtonClicked(self):
        if self.MinusRadio.isChecked():
            self.DifferenceCalculate()
        else:
            self.SumCalculate()

    @sendDataToLogger
    def SumCalculate(self):
        sumNames = sorted([item.text() for item in self.PMList.selectedItems()])
        sumStr = 'Sm_' + '_'.join(sumNames)
        if sumStr not in self.sumCols:
            dfColumns = [f'{name}' for name in sumNames]
            self.baseDf[sumStr] = self.baseDf[dfColumns[0]]
            for col in dfColumns[1:]:
                self.baseDf[sumStr] += self.baseDf[col]
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf[sumStr] = self.baseDf[sumStr]
            self.sumCols.append(sumStr)
            self.PMAdded.addItem(sumStr)
            self.refreshLists()
            self.PMListClear()
            if not self.PMAdded.isEnabled():
                self.PMAdded.setEnabled(True)
            if not self.PMRemoveCol.isEnabled():
                self.PMRemoveCol.setEnabled(True)
            self.eColumns.append(sumStr)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {sumStr} has been added.')
        else:
            self.addMessage('Column has already been added!')

    @sendDataToLogger
    def DifferenceCalculate(self):
        first, second = [item.text() for item in self.PMList.selectedItems()]
        differenceStr = 'Df_' + '-'.join([first, second])
        if differenceStr not in self.differenceCols:
            self.baseDf[differenceStr] = self.baseDf[first] - self.baseDf[second]
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf[differenceStr] = self.baseDf[differenceStr]
            self.differenceCols.append(differenceStr)
            self.PMAdded.addItem(differenceStr)
            self.refreshLists()
            self.PMListClear()
            if not self.PMAdded.isEnabled():
                self.PMAdded.setEnabled(True)
            if not self.PMRemoveCol.isEnabled():
                self.PMRemoveCol.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.eColumns.append(differenceStr)
            self.addMessage(f'Column {differenceStr} has been added.')
        else:
            self.addMessage('Column has already been added!')

    @sendDataToLogger(operationType='user')
    def PMChooseToRemove(self, *args):
        self.PMRemoveCol.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def AngleListAction(self, element):
        selectedColumns = self.AngleList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 0:
            self.AngleAddCol.setDisabled(True)
        elif listSize == 1:
            self.AnglePlaneXY.setEnabled(True)
            self.AnglePlaneYZ.setEnabled(True)
            self.AnglePlaneZX.setEnabled(True)
            self.AngleAddCol.setEnabled(True)
        elif listSize == 2:
            self.AnglePlaneXY.setDisabled(True)
            self.AnglePlaneYZ.setDisabled(True)
            self.AnglePlaneZX.setDisabled(True)
            self.AngleAddCol.setDisabled(True)
        elif listSize == 3:
            self.AngleAddCol.setEnabled(True)

        if listSize > 3:
            self.AngleList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.AngleSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    @sendDataToLogger
    def AngleListClear(self, *args):
        self.AngleSelected.clear()
        self.AngleList.clearSelection()
        self.AngleAddCol.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def AngleButtonClicked(self):
        colsNumber = len(self.AngleList.selectedItems())
        if colsNumber == 1:
            self.AngleCalculate()
        elif colsNumber == 3:
            self.ValenceAngleCalculate()

    @sendDataToLogger
    def AngleCalculate(self):
        atom = self.AngleList.selectedItems()[0].text()
        angle, plane = [], ''
        if self.AnglePlaneXY.isChecked():
            plane = 'xy'
        elif self.AnglePlaneYZ.isChecked():
            plane = 'yz'
        else:
            plane = 'zx'
        if f'{atom}_{plane}' not in self.angleCols:
            self.baseDf[f'{atom}_{plane}'] = np.degrees(np.arccos(np.sqrt(self.baseDf[f'{atom}_{plane[0]}'].diff() ** 2 + self.baseDf[f'{atom}_{plane[1]}'].diff() ** 2) / np.sqrt(self.baseDf[f'{atom}_x'].diff() ** 2 + self.baseDf[f'{atom}_y'].diff() ** 2 + self.baseDf[f'{atom}_z'].diff() ** 2)))
            self.mainDf.insert(len(self.mainDf.columns), f'{atom}_{plane}', self.baseDf[f'{atom}_{plane}'])
            self.angleCols.append(f'{atom}_{plane}')
            self.AngleAdded.addItem(f'{atom}_{plane}')
            if not self.AngleAdded.isEnabled():
                self.AngleAdded.setEnabled(True)
            if not self.AngleRemoveCol.isEnabled():
                self.AngleRemoveCol.setEnabled(True)
            self.refreshLists()
            self.AngleListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f"Column {atom}_{plane} has been added.")
        else:
            self.addMessage('Column already exists.')

    @sendDataToLogger
    def ValenceAngleCalculate(self):
        atoms = [item.text() for item in self.AngleList.selectedItems()]
        if f'{atoms[0]}-{atoms[1]}-{atoms[2]}' not in self.angleCols:
            self.baseDf[f'{atoms[0]}--{atoms[2]}'] = sum([(self.baseDf[f'{atoms[0]}{proj}'] - self.baseDf[f'{atoms[2]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])
            self.baseDf[f'{atoms[0]}--{atoms[1]}'] = sum([(self.baseDf[f'{atoms[0]}{proj}'] - self.baseDf[f'{atoms[1]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])
            self.baseDf[f'{atoms[1]}--{atoms[2]}'] = sum([(self.baseDf[f'{atoms[1]}{proj}'] - self.baseDf[f'{atoms[2]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])

            self.baseDf[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'] = np.round(np.degrees(np.arccos((self.baseDf[f'{atoms[0]}--{atoms[1]}'] + self.baseDf[f'{atoms[1]}--{atoms[2]}'] - self.baseDf[f'{atoms[0]}--{atoms[2]}']) / (2 * self.baseDf[f'{atoms[0]}--{atoms[1]}'] ** 0.5 * self.baseDf[f'{atoms[1]}--{atoms[2]}'] ** 0.5))), 2)

            self.baseDf.drop(columns=[f'{atoms[0]}--{atoms[2]}', f'{atoms[0]}--{atoms[1]}', f'{atoms[1]}--{atoms[2]}'], inplace=True)

            self.mainDf.insert(len(self.mainDf.columns), f'{atoms[0]}-{atoms[1]}-{atoms[2]}', self.baseDf[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'])
            self.angleCols.append(f'{atoms[0]}-{atoms[1]}-{atoms[2]}')
            self.AngleAdded.addItem(f'{atoms[0]}-{atoms[1]}-{atoms[2]}')
            if not self.AngleAdded.isEnabled():
                self.AngleAdded.setEnabled(True)
            if not self.AngleRemoveCol.isEnabled():
                self.AngleRemoveCol.setEnabled(True)
            self.refreshLists()
            self.AngleListClear()
            if not self.AnglePlaneXY.isEnabled():
                self.AnglePlaneXY.setEnabled(True)
                self.AnglePlaneYZ.setEnabled(True)
                self.AnglePlaneZX.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f"Column {atoms[0]}-{atoms[1]}-{atoms[2]} has been added.")
        else:
            self.addMessage('Column already exists.')

    @sendDataToLogger(operationType='user')
    def AngleChooseToRemove(self, *args):
        self.AngleRemoveCol.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def DivideListAction(self, element):
        selectedColumns = self.DivideList.selectedItems()
        listSize = len(selectedColumns)

        if listSize > 1 and not self.DivideAddCol.isEnabled():
            self.DivideAddCol.setEnabled(True)
        elif listSize == 1 and self.DivideAddCol.isEnabled():
            self.DivideAddCol.setDisabled(True)

        if listSize > 2:
            self.DivideList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.DivideSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    @sendDataToLogger
    def DivideListClear(self, *args):
        self.DivideSelected.clear()
        self.DivideList.clearSelection()
        self.DivideAddCol.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def DivideButtonClicked(self):
        self.DivideCalculate()

    @sendDataToLogger
    def DivideCalculate(self):
        temporaryCols = []
        atoms = sorted([item.text() for item in self.DivideList.selectedItems()])
        colName = '_'.join(atoms)
        if colName not in self.divideCols:
            self.COMCalculate(atoms)
            for atom in atoms:
                self.baseDf[f'cm_{colName}--{atom}'] = np.sqrt((self.baseDf[f'cm_{colName}_x'] - self.baseDf[f'{atom}_x']) ** 2 + (self.baseDf[f'cm_{colName}_y'] - self.baseDf[f'{atom}_y']) ** 2 + (self.baseDf[f'cm_{colName}_z'] - self.baseDf[f'{atom}_z']) ** 2)
                temporaryCols.append(f'cm_{colName}--{atom}')
            for atom in atoms:
                self.baseDf[f'Vvib_{colName}({atom})'] = self.baseDf[f'cm_{colName}--{atom}'].diff() * 1000
                self.divineOnPOTIM(f'Vvib_{colName}({atom})', True)
                self.baseDf[f'Evib_{colName}({atom})'] = self.baseDf[f'Vvib_{colName}({atom})'] ** 2 * self._masses[self.columnsNames.index(atom)] / self.calc_const
                self.baseDf[f'Vsum_{colName}({atom})'] = np.sqrt((self.baseDf[f'{atom}_x'].diff() - self.baseDf[f'cm_{colName}_x'].diff()) ** 2 + (self.baseDf[f'{atom}_y'].diff() - self.baseDf[f'cm_{colName}_y'].diff()) ** 2 + (self.baseDf[f'{atom}_z'].diff() - self.baseDf[f'cm_{colName}_z'].diff()) ** 2) * 1000
                self.divineOnPOTIM(f'Vsum_{colName}({atom})', True)
                self.baseDf[f'Vrot_{colName}({atom})'] = np.sqrt((self.baseDf[f'Vsum_{colName}({atom})'] ** 2 - self.baseDf[f'Vvib_{colName}({atom})'] ** 2).clip(lower=0))
                self.baseDf[f'Erot_{colName}({atom})'] = self.baseDf[f'Vrot_{colName}({atom})'] ** 2 * self._masses[self.columnsNames.index(atom)] / self.calc_const
                self.eColumns.extend([f'Evib_{colName}({atom})', f'Erot_{colName}({atom})'])
                temporaryCols.extend([f'Vvib_{colName}({atom})', f'Vsum_{colName}({atom})', f'Vrot_{colName}({atom})'])
                if not self.ADel_energy_of_sel_atoms.isChecked():
                    self.mainDf.insert(len(self.mainDf.columns), f'Evib_{colName}({atom})', self.baseDf[f'Evib_{colName}({atom})'])
                    self.mainDf.insert(len(self.mainDf.columns), f'Erot_{colName}({atom})', self.baseDf[f'Erot_{colName}({atom})'])
            self.baseDf[f'Evib_{colName}'] = sum(self.baseDf[f'Evib_{colName}({atom})'] for atom in atoms)
            self.baseDf[f'Erot_{colName}'] = sum(self.baseDf[f'Erot_{colName}({atom})'] for atom in atoms)
            self.baseDf.drop(columns=temporaryCols, inplace=True)
            temporaryCols.clear()
            self.eColumns.extend([f'Evib_{colName}', f'Erot_{colName}'])
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.insert(len(self.mainDf.columns), f'Evib_{colName}', self.baseDf[f'Evib_{colName}'])
                self.mainDf.insert(len(self.mainDf.columns), f'Erot_{colName}', self.baseDf[f'Erot_{colName}'])

            self.divideCols.append(colName)
            self.DivideAdded.addItem(colName)
            if not self.DivideAdded.isEnabled():
                self.DivideAdded.setEnabled(True)
            if not self.DivideRemoveCol.isEnabled():
                self.DivideRemoveCol.setEnabled(True)
            self.refreshLists()
            self.DivideListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Columns divided to vibrational and rotational energy {colName} have been added.')
        else:
            self.addMessage('Column already exists.')

    @sendDataToLogger(operationType='user')
    def DivideChooseToRemove(self, *args):
        self.DivideRemoveCol.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def renameColumnChoose(self):
        colName = self.RenameSelect.currentText()
        if colName:
            self.RenameLine.setText(colName)
            self.RenameLine.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def renameColumnAction(self):
        if self.RenameSelect.currentText() != self.RenameLine.text():
            self.RenameButton.setEnabled(True)
        else:
            self.RenameButton.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def renameColumn(self):
        newName = self.RenameLine.text()
        oldName = self.RenameSelect.currentText()
        for array in [self.eColumns, self.distanceCols, self.angleCols, self.sumCols, self.differenceCols]:
            for column in array.copy():
                if column == oldName:
                    array[array.index(column)] = newName
        self.baseDf.rename(columns={oldName: newName}, inplace=True)
        self.mainDf.rename(columns={oldName: newName}, inplace=True)
        self.refreshLists()
        self._model.refreshTable(self.mainDf)
        self.addMessage(f'Column {oldName} has been renamed. New name is {newName}.')

    @sendDataToLogger(operationType='user')
    def delCoordsAction(self, state):
        if state:
            for name in self.columnsNames:
                for proj in ['_x', '_y', '_z']:
                    self.mainDf.drop(columns=f'{name}{proj}', inplace=True)
            self.refreshLists()
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with coordinates of atoms have been removed.')
        else:
            for name in reversed(self.columnsNames):
                for proj in reversed(['_x', '_y', '_z']):
                    self.mainDf.insert(1, name + proj, self.baseDf[name + proj])
            self.refreshLists()
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with coordinates of atoms have been added.')

    @sendDataToLogger(operationType='user')
    def delEnergyAction(self, state):
        if state:
            self.mainDf.drop(columns=self.eColumns, inplace=True)
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with energy have been removed.')
        else:
            for column in self.eColumns:
                self.mainDf.insert(len(self.mainDf.columns), column, self.baseDf[column])
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with energy have been added.')

    @sendDataToLogger(operationType='user')
    def columnSelected(self, selected, deselected):
        selected_list = selected.toList()
        deselected_list = deselected.toList()
        if selected_list and not selected_list[0].top() and selected_list[0].bottom() == len(self.mainDf) - 1 and selected_list[0].left() == selected_list[0].right():
            self._selected_columns.append(selected_list[0].left())
            self._selected_columns.sort()
        if deselected_list and self._selected_columns and not deselected_list[0].top():
            for column in deselected_list:
                self._selected_columns.remove(column.left())
        if self._selected_columns:
            self.PlotGraphButton.setEnabled(True)
        else:
            self.PlotGraphButton.setDisabled(True)

    @sendDataToLogger(operationType='user')
    def plotGraph(self):
        columns_indexes = [column.column() for column in self._selectionModel.selectedColumns()]
        df = pd.DataFrame(self.mainDf[self.mainDf.columns[0]])
        for index in columns_indexes:
            df[self.mainDf.columns[index]] = self.mainDf[self.mainDf.columns[index]]
        self.__graph = VRGraph(df)
        self.PlotGraphButton.setDisabled(True)
        self._selectionModel.clearSelection()

    @sendDataToLogger
    def oszicarCheckboxUnlock(self):
        files = os.listdir(self.__calculation['DIRECTORY'])
        for file in files:
            if 'OSZICAR' in file:
                self.AInclude_OSZICAR.setEnabled(True)
                break

    @sendDataToLogger(operationType='user')
    def oszicarAction(self, state):
        if state:
            oszicarDataframe = VROszicarProcessing(self.__calculation['DIRECTORY'], self.getLogger(), self.__calculation['STEPS_LIST'], self.__calculation['POTIM']).oszicarDf
            self.mainDf = pd.concat([self.mainDf, oszicarDataframe[oszicarDataframe.columns[1:]]], axis=1)
            self.addMessage('OSZICAR dataframe has been added.')
            self._model.refreshTable(self.mainDf)
        else:
            self.mainDf.drop(columns=['T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'], inplace=True)
            self.addMessage('OSZICAR dataframe has been removed.')
            self._model.refreshTable(self.mainDf)

    @sendDataToLogger(operationType='user')
    def saveTable(self):
        tableDir = QFileDialog.getSaveFileName(None, caption='Save Table', filter="Excel (*.xlsx *.xls);;Csv (*.csv);;HTML (*.html)", selectedFilter="Excel (*.xlsx *.xls)")[0]
        if tableDir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tableDir)
                self.mainDf.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.mainDf:
                    column_width = max(self.mainDf[column].astype(str).map(len).max(), len(column))
                    col_idx = self.mainDf.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(col_idx, col_idx, column_width)
                writer.close()
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.addMessage('Close Excel table before writing.') # title='OpenXslError')
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.csv'):
            try:
                self.mainDf.to_csv(tableDir, index=False)
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.html'):
            try:
                self.mainDf.to_html(tableDir, index=False, na_rep='')
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())

    def graphWindow(self):
        ...
