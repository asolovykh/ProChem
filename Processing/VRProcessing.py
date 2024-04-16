import os
import traceback
import numpy as np
import pandas as pd
from Gui.VRProcessingGUI import Ui_VRProcessing, QMainWindow
from PySide6.QtCore import Qt, QAbstractTableModel, QItemSelectionModel
from PIL import Image, ImageTk, ImageSequence
from Logs.VRLogger import sendDataToLogger


class VRPdModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def refreshTable(self, df):
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return f'{self._data.values[index.row()][index.column()]:f}'
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def insertColumn(self, column, place, parent=None):
        self.beginInsertColumns(parent, place, place)
        self.endInsertColumns()

    def insertRow(self, row, place, parent=None):
        self.beginInsertRows(parent, place, place)
        self.endInsertRows()

    def removeColumn(self, column, place, parent=None):
        self.beginRemoveColumns(parent, place, place)
        self.endRemoveColumns()

    def removeRow(self, column, place, parent=None):
        self.beginRemoveRows(parent, place, place)
        self.endRemoveRows()


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
        location = self.__settings.processing_window_location
        self.__parent = visualWindowObject
        self.__logger = printWindowObject
        self.__openGl = openGlWindowObject
        self.setupUi(self)
        self.linkElementsWithFunctions()
        if location is not None:
            self.move(location[0], location[1])
        self.__calculation = calculation
        self._deleteAfterLeave = deleteAfterLeave
        self._name = name
        self._selected_atoms = self.__calculation['ATOMNAMES']

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
        else:
            self.mainDf = pd.DataFrame()
            timeArr = np.arange(0, float(self.__calculation['POTIM'][0]) * self.__calculation['STEPS_LIST'][0], float(self.__calculation['POTIM'][0]))
            for index, steps in enumerate(self.__calculation['STEPS_LIST'][1:], start=1):
                addTimeArr = np.arange(timeArr[-1] + float(self.__calculation['POTIM'][index]), timeArr[-1] + float(self.__calculation['POTIM'][index]) * steps, float(self.__calculation['POTIM'][index]))
                timeArr = np.concatenate([timeArr, addTimeArr])
            self.mainDf.insert(0, 'Time, fs', timeArr[:self.__calculation['STEPS']])
        self._model = VRPdModel(self.mainDf)
        self.ViewTable.setModel(self._model)
        self.__parent.hide()
        self.__openGl.hide()

    def getLogger(self):
        return self.__logger

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

    @sendDataToLogger
    def closeEvent(self, event):
        self.__parent.show()
        self.__openGl.show()
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
        for step in range(self.__calculation['STEPS']):
            temp, counter = [], 0
            for atom_num in range(self.__calculation['ATOMNUMBER']):
                if 'Sel' in self._selected_atoms[atom_num]:
                    if step > 0:
                        badColumns = self.atomAway(self.__calculation['DIRECT'][step][atom_num], data[step - 1][counter])
                        if badColumns:
                            temp.append(self.atomAwayColumnsFix(data, counter, badColumns, step, atom_num))
                        else:
                            temp.append(self.__calculation['DIRECT'][step][atom_num])
                        del badColumns
                    else:
                        temp.append(self.__calculation['DIRECT'][step][atom_num])
                    counter += 1
            data.append(temp.copy())
            del temp
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
    def atomAway(direct, data):
        badColumns = []
        for num, _ in enumerate(direct):
            if direct[num] - data[num] > 0.9:
                badColumns.append((num, 'minus'))
            elif data[num] - direct[num] > 0.9:
                badColumns.append((num, 'plus'))
        return badColumns

    @sendDataToLogger
    def atomAwayColumnsFix(self, data, counter, badColumns, step, atom_num):
        newCol = self.__calculation['DIRECT'][step][atom_num].tolist()
        for num, operation in badColumns:
            exprFactor = round(abs(self.__calculation['DIRECT'][step][atom_num][num] - data[step - 1][counter][num]))
            if operation == 'plus':
                newCol[num] = newCol[num] + exprFactor
            else:
                newCol[num] = newCol[num] - exprFactor
        return np.array(newCol)

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

    @sendDataToLogger(operation_type='user')
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
            self.getLogger().addMessage(f'Column {toDelete} has been removed.', self.__class__.__name__)
        elif colsList == self.sumCols or colsList == self.differenceCols:
            self.baseDf.drop(columns=toDelete, inplace=True)
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDelete, inplace=True)
            colsList.remove(toDelete)
            self.eColumns.remove(toDelete)
            self.getLogger().addMessage(f'Column {toDelete} has been removed.', self.__class__.__name__)
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
            self.getLogger().addMessage(f'Columns divided to vibrational and rotational energy {toDelete} have been removed.', self.__class__.__name__)
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
            self.getLogger().addMessage(f'Column {self.eColumns[-1]} and linked columns have been removed.', self.__class__.__name__)
            self.eColumns.remove(f'E{toDelete}')
            self.columnsNames.remove(toDelete)
            self.weightmassCols.remove(toDelete)
        addedColsElement.removeItem(addedColsElement.currentIndex())
        if not addedColsElement.count():
            addedColsElement.setDisabled(True)
            removeElement.setDisabled(True)
        self.refreshLists()
        self._model.refreshTable(self.mainDf)

    @sendDataToLogger(operation_type='user')
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

    @sendDataToLogger(operation_type='user')
    def DCButtonClicked(self):
        if self.DistanceRadio.isChecked():
            self.DistanceCalculate()
        else:
            self.COMCalculate()

    @sendDataToLogger
    def DistanceCalculate(self):
        first, second = sorted([item.text() for item in self.DCList.selectedItems()])
        if f'{first}--{second}' in self.baseDf:
            self.getLogger().addMessage('Column has already been added!', self.__class__.__name__, result='FAILED', cause='Column has already been added')
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
            self.getLogger().addMessage(f'Column {first}--{second} has been added.', self.__class__.__name__)

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
            self.getLogger().addMessage(f'Column {self.eColumns[-1]} has been added.', self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column has already been added!', self.__class__.__name__, result='FAILED', cause='Column has already been added')
            self.DCListClear()

    @sendDataToLogger(operation_type='user')
    def DCChooseToRemove(self, *args):
        self.DCRemoveCol.setEnabled(True)

    @sendDataToLogger(operation_type='user')
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

    @sendDataToLogger(operation_type='user')
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
            self.getLogger().addMessage(f'Column {sumStr} has been added.', self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column has already been added!', self.__class__.__name__)

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
            self.getLogger().addMessage(f'Column {differenceStr} has been added.', self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column has already been added!', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def PMChooseToRemove(self, *args):
        self.PMRemoveCol.setEnabled(True)

    @sendDataToLogger(operation_type='user')
    def AngleListAction(self, element):
        selectedColumns = self.AngleList.selectedItems()
        listSize = len(selectedColumns)

        if listSize < 2 and self.AnglePlaneXY.isEnabled():
            self.AnglePlaneXY.setEnabled(True)
            self.AnglePlaneYZ.setEnabled(True)
            self.AnglePlaneZX.setEnabled(True)
            self.AngleAddCol.setEnabled(True)
        elif listSize == 2 and not self.AnglePlaneXY.isEnabled():
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

    @sendDataToLogger(operation_type='user')
    def AngleButtonClicked(self):
        colsNumber = self.AngleList.count()
        if colsNumber == 1:
            self.AngleCalculate()
        else:
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
            self.getLogger().addMessage(f"Column {atom}_{plane} has been added.", self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column already exists.', self.__class__.__name__)

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
            self._model.refreshTable(self.mainDf)
            self.getLogger().addMessage(f"Column {atoms[0]}-{atoms[1]}-{atoms[2]} has been added.", self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column already exists.', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def AngleChooseToRemove(self, *args):
        self.AngleRemoveCol.setEnabled(True)

    @sendDataToLogger(operation_type='user')
    def DivideListAction(self, element):
        selectedColumns = self.DivideList.selectedItems()
        listSize = len(selectedColumns)

        if listSize > 1 and not self.DivideAddCol.isEnabled():
            self.DivideAddCol.setEnabled(True)
        elif listSize == 1 and self.DivideAddCol.isEnabled():
            self.DivideAddCol.setDisabled(True)

        self.DivideSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    @sendDataToLogger
    def DivideListClear(self, *args):
        self.DivideSelected.clear()
        self.DivideList.clearSelection()
        self.DivideAddCol.setDisabled(True)

    @sendDataToLogger(operation_type='user')
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
                if not self.value['EnergyCheck']:
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
            self.AngleListClear()
            self._model.refreshTable(self.mainDf)
            self.getLogger().addMessage(f'Columns divided to vibrational and rotational energy {colName} have been added.', self.__class__.__name__)
        else:
            self.getLogger().addMessage('Column already exists.', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def DivideChooseToRemove(self, *args):
        self.DivideRemoveCol.setEnabled(True)

    @sendDataToLogger
    def oszicarCheckboxUnlock(self):
        files = os.listdir(self.__calculation['DIRECTORY'])
        for file in files:
            if 'OSZICAR' in file:
                self.window['OSZICARcheck'].update(disabled=False)
                break

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

    def save_table(self):
        tabledir = sg.PopupGetFile(message='Input directory to save table', title='Save table', save_as=True,
                                   no_window=True, keep_on_top=True, default_extension=self.name, default_path=self.name,
                                   file_types=(("Excel File", "*.xlsx"), ("Csv File", "*.csv"), ("Html File", "*.html")))
        if tabledir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tabledir)
                self.mainDf.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.mainDf:
                    column_width = max(self.mainDf[column].astype(str).map(len).max(), len(column))
                    col_idx = self.mainDf.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(col_idx, col_idx, column_width)
                writer.close()
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.popup('Close Excel table before writing.', title='OpenXslError')
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.csv'):
            try:
                self.mainDf.to_csv(tabledir, index=False)
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.html'):
            try:
                self.mainDf.to_html(tabledir, index=False, na_rep='')
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')

    def mainloop(self):
        # self.window['TablePreview'].update(list(self.mainDf.columns))
        self.window.perform_long_operation(lambda: self.window['TablePreview'].update(preview_columns_form(self.mainDf)), end_key='None')
        while True:
            self.event, self.value = self.window.read()
            if self.event == sg.WINDOW_CLOSED or self.event == 'Exit':
                self.window.close()
                self.print('Processing window has been closed.')
                break
            if self.event == 'CreateExcel':
                self.save_table()
            if self.event == 'TableActiveCheck':
                if not self.value['TableActiveCheck']:
                    self.window['TablePreview'].update('', disabled=True)
                    self.print('Table preview has been turned off.')
                else:
                    self.window['TablePreview'].update(preview_columns_form(self.mainDf), disabled=True)
                    self.print('Table preview has been turned on.')
            if self.event == 'DelCoordCheck':
                if self.value['DelCoordCheck']:
                    for name in self.columnsNames:
                        for proj in ['_x', '_y', '_z']:
                            self.mainDf.drop(columns=f'{name}{proj}', inplace=True)
                    self.print('Columns with coordinates of atoms have been removed.')
                    self.update_choose_elements()
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))
                else:
                    for name in reversed(self.columnsNames):
                        for proj in reversed(['_x', '_y', '_z']):
                            self.mainDf.insert(1, name + proj, self.baseDf[name + proj])
                    self.print('Columns with coordinates of atoms have been added.')
                    self.update_choose_elements()
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))

            if self.event == 'OSZICARcheck':
                if self.value['OSZICARcheck']:
                    osz_dataframe = VROszicarProcessing(self.calculation['DIRECTORY'], self.calculation['STEPS_LIST'], self.calculation['POTIM']).oszicar_df
                    self.mainDf = pd.concat([self.mainDf, osz_dataframe[osz_dataframe.columns[1:]]], axis=1)
                    self.print('OSZICAR dataframe has been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))
                else:
                    self.mainDf.drop(columns=['T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'], inplace=True)
                    self.print('OSZICAR dataframe has been removed.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))

            if self.event == 'EnergyCheck':
                if self.value['EnergyCheck']:
                    self.mainDf.drop(columns=self.eColumns, inplace=True)
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))
                    self.print('Columns with energy have been removed.')
                else:
                    for column in self.eColumns:
                        self.mainDf.insert(len(self.mainDf.columns), column, self.baseDf[column])
                    self.print('Columns with energy have been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.mainDf))

            if self.event == 'DistAtoms':
                self.distance_names_selected = self.two_variants_listbox_click(self.distance_names_selected, 'DistAtoms', 'DistList', 'AddDist', ', ', True)
            if self.event == 'AddDist':
                self.distance_add()
            if self.event == 'DistAdded':
                if self.value['DistAdded'] != '':
                    self.window['RemoveDist'].update(disabled=False)
            if self.event == 'RemoveDist':
                self.removeColumns('DistAdded', 'RemoveDist', self.distanceCols)

            if self.event == 'AtomAngle':
                self.angle_listbox_event()
            if self.event == 'xy':
                self.angle_plane_events('xy', 'yz', 'zx')
            if self.event == 'yz':
                self.angle_plane_events('yz', 'xy', 'zx')
            if self.event == 'zx':
                self.angle_plane_events('zx', 'xy', 'yz')
            if self.event == 'AddAngle':
                if len(self.angle_names_selected) == 1:
                    self.angle_add()
                elif len(self.angle_names_selected) == 3:
                    self.valence_angle_add()
            if self.event == 'AngleAdded':
                if self.value['AngleAdded'] != '':
                    self.window['RemoveAngle'].update(disabled=False)
            if self.event == 'RemoveAngle':
                self.removeColumns('AngleAdded', 'RemoveAngle', self.angleCols)

            if self.event == 'WeightAtom':
                if len(self.value['WeightAtom']) > 1:
                    self.window['AddAtomWeight'].update(disabled=False)
                else:
                    self.window['AddAtomWeight'].update(disabled=True)
                self.window['WeightList'].update(', '.join(self.value['WeightAtom']))
            if self.event == 'AddAtomWeight':
                self.weight_add()
            if self.event == 'COMAdded':
                if self.value['COMAdded'] != '':
                    self.window['RemoveAtomWeight'].update(disabled=False)
            if self.event == 'RemoveAtomWeight':
                self.remove_COM()

            if self.event == 'SumAtom':
                if len(self.value['SumAtom']) > 1:
                    self.window['AddAtomSum'].update(disabled=False)
                else:
                    self.window['AddAtomSum'].update(disabled=True)
                self.window['SumList'].update(', '.join(self.value['SumAtom']))
            if self.event == 'AddAtomSum':
                self.sum_add()
            if self.event == 'SumAdded':
                if self.value['SumAdded'] != '':
                    self.window['RemoveAtomSum'].update(disabled=False)
            if self.event == 'RemoveAtomSum':
                self.remove_sum()

            if self.event == 'MinusAtom':
                self.difference_names_selected = self.two_variants_listbox_click(self.difference_names_selected, 'MinusAtom', 'MinusList', 'AddAtomMinus', '---', False)
            if self.event == 'AddAtomMinus':
                self.difference_add()
            if self.event == 'MinusAdded':
                if self.value['MinusAdded'] != '':
                    self.window['RemoveAtomMinus'].update(disabled=False)
            if self.event == 'RemoveAtomMinus':
                self.remove_difference()

            if self.event == 'DivideAtoms':
                self.divide_names_selected = self.two_variants_listbox_click(self.divide_names_selected, 'DivideAtoms', 'DivideList', 'AddAtomsDivide', ', ', True)
            if self.event == 'AddAtomsDivide':
                self.divide_add()
            if self.event == 'DivideAdded':
                if self.value['DivideAdded'] != '':
                    self.window['RemoveAtomsDivide'].update(disabled=False)
            if self.event == 'RemoveAtomsDivide':
                self.remove_divide()

            if self.event == 'RenameColChoose':
                self.window['RenameInput'].update(self.value['RenameColChoose'], disabled=False)
            if self.event == 'RenameInput':
                if self.value['RenameInput'] != self.value['RenameColChoose']:
                    self.window['RenameSubmit'].update(disabled=False)
                else:
                    self.window['RenameSubmit'].update(disabled=True)
            if self.event == 'RenameSubmit':
                name = self.value['RenameInput']
                for array in [self.eColumns, self.distanceCols, self.angleCols, self.sumCols, self.differenceCols, self.divide_names_selected, self.distance_names_selected, self.difference_names_selected]:
                    for column in array.copy():
                        if column == self.value['RenameColChoose']:
                            array[array.index(column)] = name
                self.baseDf.rename(columns={self.value['RenameColChoose']: name}, inplace=True)
                self.mainDf.rename(columns={self.value['RenameColChoose']: name}, inplace=True)
                if self.value['TableActiveCheck']:
                    self.window['TablePreview'].update(preview_columns_form(self.mainDf))
                self.print(f'Column {self.value["RenameColChoose"]} has been renamed. New name is {name}.')
                self.update_choose_elements()

            if self.event == 'RenameImage':
                if self.show_ester_egg < 4:
                    self.print('Nothing here.')
                    self.show_ester_egg += 1
                elif self.show_ester_egg == 4:
                    self.print('Do you really hope to find something clicking this image?')
                    self.show_ester_egg += 1
                elif self.show_ester_egg == 5:
                    self.print('Come on. Click it much stronger.')
                    self.show_ester_egg += 1
                elif 5 < self.show_ester_egg < 10:
                    self.show_ester_egg += 1
                else:
                    self.print('Wow wow, you are really crazy. Okay, I\'l show you something interesting!')
                    self.show_ester_egg = 0
                    window = VRGUI(egg_window, title='Something fine', location=self.window.current_location(), element_justification='c', margins=(0, 0), element_padding=(0, 0)).window_return()
                    gif_filename = 'Debug_Wallpaper\\starwars.gif'

                    interframe_duration = Image.open(gif_filename).info['duration']  # get how long to delay between frames
                    win_closed = False
                    while True:
                        for frame in ImageSequence.Iterator(Image.open(gif_filename)):
                            event, values = window.read(timeout=interframe_duration)
                            if event == sg.WIN_CLOSED:
                                win_closed = True
                                break
                            window['-EGGIMAGE-'].update(data=ImageTk.PhotoImage(frame))
                        if win_closed:
                            break

            if self.event == 'GraphMode':
                self.window.hide()
                self.print('Entering graph window.')
                VRGraphsProcessing(self.mainDf, theme=self.theme).mainloop()
                self.window.un_hide()
