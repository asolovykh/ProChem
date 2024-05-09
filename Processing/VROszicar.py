from Logs.VRLogger import sendDataToLogger
from Gui.VROszicarGUI import Ui_VROszicar, QMainWindow
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QAbstractTableModel, QItemSelectionModel
import os
import traceback
import pandas as pd


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


class VROszicarProcessing:
    def __init__(self, directory, printWindowObject, steps, POTIM):
        self.__logger = printWindowObject
        self.directory, self.steps = directory, steps
        self.directoryFiles = os.listdir(directory)
        self.oszicarFiles, self.data, self.POTIM, self.oszicarDf = [], [], POTIM, pd.DataFrame()
        self.oszicarSearch()
        if self.oszicarFiles:
            self.formOszicarDataframe()
        else:
            self.addMessage('No OSZICAR files in directory.')

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger
    def oszicarSearch(self):
        for file in self.directoryFiles:
            if 'OSZICAR' in file:
                self.oszicarFiles.append(file)
        if self.oszicarFiles:
            self.oszicarFiles.sort()
        if 'OSZICAR' in self.oszicarFiles:
            self.oszicarFiles.append(self.oszicarFiles[0])
            self.oszicarFiles.pop(0)

    @sendDataToLogger
    def oszicarParse(self, index):
        if index > 0:
            startCount = self.data[-1][0]
        else:
            startCount = 0
        with open(f'{self.directory}/{self.oszicarFiles[index]}', 'r') as osz:
            while True:
                line = osz.readline()
                if not line:
                    break
                else:
                    if 'T' in line and 'mag' in line:
                        startCount += 1
                        addToData = [startCount]
                        addToData.extend(list(map(float, line.split()[2::2])))
                        self.data.append(list(addToData))
                        del addToData
        if self.POTIM:
            prevIndex = 0
            for index, POTIM in enumerate(self.POTIM):
                for dataIndex in range(prevIndex, self.steps[index]):
                    self.data[dataIndex][0] = self.data[dataIndex][0] * POTIM
                prevIndex = self.steps[index]
        self.data.pop(-1)
        self.data.pop(-1)

    @sendDataToLogger
    def formOszicarDataframe(self):
        for index in range(len(self.oszicarFiles)):
            self.oszicarParse(index)
        self.oszicarFillToNormalLen()
        self.oszicarDf = pd.DataFrame(self.data, columns=['Time, fs', 'T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'])

    @sendDataToLogger
    def oszicarFillToNormalLen(self):
        if self.steps:
            while len(self.data) != self.steps[-1] - 2:
                if len(self.data) > self.steps[-1] - 2:
                    self.data.pop(-1)
                else:
                    self.data.append([None for _ in range(9)])


class VROszicar(Ui_VROszicar, QMainWindow):
    def __init__(self, directory, app, settings, visualWindowObject, openGLWindow, printWindowObject):
        super(VROszicar, self).__init__()
        self.__app = app
        self.__settings = settings
        self.__logger = printWindowObject
        self.directory = directory
        location = self.__settings.oszicarWindowLocation
        self.__parent = visualWindowObject
        self.__openGLWindow = openGLWindow
        self.setupUi(self)
        self.linkElementsWithFunctions()
        if location is not None:
            self.move(location[0], location[1])
        self.oszicarDf = VROszicarProcessing(directory, printWindowObject, [], []).oszicarDf
        self._model = VRPdModel(self.oszicarDf)
        self.OszicarTableView.setModel(self._model)
        self.__parent.hide()
        self.__openGLWindow.hide()

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger
    def closeAll(self, event):
        self.__parent.close()
        event.accept()

    @sendDataToLogger
    def closeEvent(self, event=QCloseEvent()):
        self.__parent.show()
        self.__openGLWindow.show()
        event.accept()

    @sendDataToLogger
    def linkElementsWithFunctions(self):
        self.OszicarCreateExcelButton.clicked.connect(self.saveTable)
        self.OszicarBack.clicked.connect(self.window().close)
        self.ABack.triggered.connect(self.window().close)
        self.AExit.triggered.connect(lambda: self.closeAll(QCloseEvent()))

    @sendDataToLogger(operationType='user')
    def saveTable(self):
        tableDir = QFileDialog.getSaveFileName(None, caption='Save Table', filter="Excel (*.xlsx *.xls);;Csv (*.csv);;HTML (*.html)", selectedFilter="Excel (*.xlsx *.xls)")[0]
        if tableDir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tableDir)
                self.oszicarDf.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.oszicarDf:
                    columnWidth = max(self.oszicarDf[column].astype(str).map(len).max(), len(column))
                    colIdx = self.oszicarDf.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(colIdx, colIdx, columnWidth)
                writer.close()
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.addMessage('Close Excel table before writing.') # title='OpenXslError')
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.csv'):
            try:
                self.oszicarDf.to_csv(tableDir, index=False)
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.html'):
            try:
                self.oszicarDf.to_html(tableDir, index=False, na_rep='')
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
