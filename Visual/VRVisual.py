import os
import codecs
import time
from multiprocessing import Process, Lock as MLock, cpu_count, Manager
from threading import Thread, Lock as TLock
from Processing.VRMD import VRMD, QEMD
from Processing.VRProcessing import VRProcessing
from Processing.VROszicar import VROszicar
from Gui.VRVisualGUI import Ui_VRVisual, QMainWindow
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QColorDialog, QFileDialog
from Logs.VRLogger import sendDataToLogger


class VRVisualWindow(Ui_VRVisual, QMainWindow):
    __cpu_count = cpu_count()

    @sendDataToLogger
    def __init__(self, app, settings, printWindowObject):
        super(VRVisualWindow, self).__init__()
        self.__logger = printWindowObject
        self.calculationFolder = None
        self.__calculations = dict()
        self.__app = app
        self.__settings = settings
        self.__projectDirectory = self.__logger.getProjectDir()
        self.parserThreads, self.parserProcesses, self.parserDicts = [], [], []
        self.threadsLocker, self.processesLocker = TLock(), MLock()
        self.isThreadingMode = True
        location = self.__settings.visualWindowLocation
        self.setupUi(self)
        self.linkElementsWithFunctions()
        if location is not None:
            self.move(location[0], location[1])
        if self.__cpu_count > 4:
            self.AThreading.setEnabled(True)
            self.AMultiprocessing.setEnabled(True)
        self.show()

        self.__openGlWindow = None
        self.__processingWindow = None
        self.__oszicarWindow = None
        self._stepSliderSpeed = 1
        self._backgroundColor = (0.6, 0.6, 0.6, 1.0)
        self._windowClosed = False
        self.parserCheckThread = Thread(target=self.checkParsers, daemon=True)
        self.parserCheckThread.start()

    def linkWithOpenGlWindow(self, windowObject):
        self.__openGlWindow = windowObject

    @sendDataToLogger
    def linkElementsWithFunctions(self):
        self.AOpen_calculation.triggered.connect(self.openCalculationFolder)
        self.ABackground.triggered.connect(self.backgroundColorChange)
        self.BrowseButton.clicked.connect(self.openCalculationFolder)
        self.AAbout_the_program.triggered.connect(self.aboutTheProgram)
        self.AAbout_window.triggered.connect(self.aboutTheWindow)
        self.ALatest_update.triggered.connect(self.lattestUpdate)
        self.AChanges_history.triggered.connect(self.changesHistory)
        self.AExit.triggered.connect(self.closeEvent)
        self.CalculationAddButton.clicked.connect(self.addCalculation)
        self.AddedCalculations.activated.connect(self.changeActiveCalculation)
        self.DeleteCalculationButton.clicked.connect(self.deleteCalculation)
        self.StepSlider.actionTriggered.connect(self.calculationStepChange)
        self.SpeedSlider.actionTriggered.connect(self.speedChange)
        self.APerspective.toggled.connect(self.perspectiveChose)
        self.AOrthographic.toggled.connect(self.orthographicChose)
        self.AKeyboard.toggled.connect(self.keyboardSelect)
        self.AMouse_keyboard.toggled.connect(self.mouseAndKeyboardSelect)
        self.MoveBack.clicked.connect(self.backwardMove)
        self.MoveForward.clicked.connect(self.forwardMove)
        self.ToFirstStep.clicked.connect(self.toFirstStep)
        self.ToLastStep.clicked.connect(self.toLastStep)
        self.VASP_Processing.triggered.connect(self.processingStart)
        self.VASP_OSZICAR.triggered.connect(self.oszicarWindow)
        self.AThreading.toggled.connect(self.settingsThreading)
        self.AMultiprocessing.toggled.connect(self.settingsMultiprocessing)

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger(operationType='user')
    def settingsMultiprocessing(self, checked):
        if checked:
            self.AThreading.setChecked(False)
            self.AMultiprocessing.setChecked(True)
        else:
            self.AThreading.setChecked(True)
            self.AMultiprocessing.setChecked(False)
        self.isThreadingMode = not checked

    @sendDataToLogger(operationType='user')
    def settingsThreading(self, checked):
        if checked:
            self.AThreading.setChecked(True)
            self.AMultiprocessing.setChecked(False)
        else:
            self.AThreading.setChecked(False)
            self.AMultiprocessing.setChecked(True)
        self.isThreadingMode = checked

    @sendDataToLogger
    def blockParserModeChanging(self):
        self.AThreading.setEnabled(False)
        self.AMultiprocessing.setEnabled(False)

    @sendDataToLogger
    def enableParserModeChanging(self):
        self.AThreading.setEnabled(True)
        self.AMultiprocessing.setEnabled(True)

    @sendDataToLogger(operationType='user')
    def toFirstStep(self):
        self.__openGlWindow._step = 0
        self.StepSlider.setSliderPosition(0)
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    @sendDataToLogger(operationType='user')
    def toLastStep(self):
        self.__openGlWindow._step = self.__calculations[self.calculationFolder]['STEPS'] - 1
        self.StepSlider.setSliderPosition(self.__calculations[self.calculationFolder]['STEPS'] - 1)
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    @sendDataToLogger(operationType='user')
    def backwardMove(self):
        self.__openGlWindow.BackStep = True
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    @sendDataToLogger(operationType='user')
    def forwardMove(self):
        self.__openGlWindow.ForwardStep = True
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    def stopStepChanging(self):
        self.__openGlWindow.BackStep = False
        self.__openGlWindow.ForwardStep = False

    @sendDataToLogger(operationType='user')
    def openCalculationFolder(self):
        self.DirectoryPath.setText(QFileDialog.getExistingDirectory(None, caption="Choose directory to parse"))

    @sendDataToLogger
    def closeEvent(self, event=QCloseEvent):
        self.__settings.visualWindowLocation = self.pos().toTuple()
        self.getLogger().close()
        self.__openGlWindow._parentWindowClosed = True
        self.getLogger()._visualWindowClosed = True
        event.accept()

    @sendDataToLogger(operationType='user')
    def keyboardSelect(self, checked, *args):
        if checked:
            self.AKeyboard.setChecked(True)
            self.AMouse_keyboard.setChecked(False)
            self.__openGlWindow.onlyKeyboardSelect = True
        else:
            self.AKeyboard.setChecked(False)
            self.AMouse_keyboard.setChecked(True)
            self.__openGlWindow.onlyKeyboardSelect = False

    @sendDataToLogger(operationType='user')
    def mouseAndKeyboardSelect(self, checked, *args):
        if checked:
            self.AKeyboard.setChecked(False)
            self.AMouse_keyboard.setChecked(True)
            self.__openGlWindow.onlyKeyboardSelect = False
            self.addMessage('Changed to mouse+keyboard mode.')
        else:
            self.AKeyboard.setChecked(True)
            self.AMouse_keyboard.setChecked(False)
            self.__openGlWindow.onlyKeyboardSelect = True
            self.addMessage('Changed to keyboard mode.')

    @sendDataToLogger(operationType='user')
    def perspectiveChose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__openGlWindow.isPerspective = True
        else:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__openGlWindow.isPerspective = False

    @sendDataToLogger(operationType='user')
    def orthographicChose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__openGlWindow.isPerspective = False
            self.addMessage('Changed to orthographic view')
        else:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__openGlWindow.isPerspective = True
            self.addMessage('Changed to perspective view')

    @sendDataToLogger(operationType='user')
    def backgroundColorChange(self):
        self._backgroundColor = tuple(QColorDialog().getColor().toTuple())
        self._backgroundColor = tuple([self._backgroundColor[i] / 255 for i in range(len(self._backgroundColor))])
        self.__openGlWindow._backgroundColor = self._backgroundColor
        self.__openGlWindow._fogColor = self._backgroundColor
        self.addMessage(f'Background color changed to {self._backgroundColor}')

    def calculationStepChange(self):
        self.stopStepChanging()
        self.__openGlWindow._step = self.StepSlider.sliderPosition()
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    def speedChange(self):
        self._stepSliderSpeed = self.SpeedSlider.sliderPosition()
        self.__openGlWindow._speed = self._stepSliderSpeed

    @sendDataToLogger(operationType='user')
    def addCalculation(self):
        self.stopStepChanging()
        self.calculationFolder = self.DirectoryPath.text()
        if self.calculationFolder and self.calculationFolder not in self.__calculations:
            if self.isThreadingMode:
                self.parserDicts.append(dict())
                self.parserThreads.append(Thread(target=VRMD, args=(self.calculationFolder, self.parserDicts[-1],), daemon=True))
                self.parserThreads[-1].start()
            else:
                self.parserDicts.append(Manager().dict())
                self.parserProcesses.append(Process(target=VRMD, args=(self.calculationFolder, self.parserDicts[-1],), daemon=True))
                self.parserProcesses[-1].start()
            self.blockParserModeChanging()

    def checkParsers(self):
        while True:
            if self.isThreadingMode and self.parserThreads:
                for num, thread in enumerate(self.parserThreads.copy()):
                    if not thread.is_alive():
                        with self.threadsLocker:
                            self.processAddAction(self.parserDicts.pop(num))
                            self.parserThreads.pop(num)
                if not self.parserThreads:
                    self.enableParserModeChanging()
            elif not self.isThreadingMode and self.parserProcesses:
                for num, process in enumerate(self.parserProcesses.copy()):
                    if not process.is_alive():
                        with self.processesLocker:
                            self.processAddAction(dict(self.parserDicts.pop(num)))
                            self.parserProcesses.pop(num)
                if not self.parserProcesses:
                    self.enableParserModeChanging()
            time.sleep(0.1)

    def processAddAction(self, parserParameters):
        directory = parserParameters['DIRECTORY']
        self.__calculations[directory] = parserParameters
        if parserParameters['BREAKER']:
            self.__calculations.pop(directory)
            self.addMessage(parserParameters['MESSAGE'], fromWindow='VRMD', result='FAILED', detailedDescription=parserParameters['MESSAGE'])
            # parserObj = QEMD(self.calculationFolder, self.getLogger())
            # self.__calculations[self.calculationFolder] = parserObj._parserParameters
        else:
            self.__openGlWindow.loadCalculationInfo(self.__calculations[directory])
            self.addMessage(f'Chosen {directory} appended.\n')
            self.AddedCalculations.addItem(directory)
            self.AddedCalculations.setCurrentText(directory)
            self.StepSlider.setMaximum(self.__calculations[directory]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__openGlWindow._step = 0
            self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    @sendDataToLogger
    def stopAllThreadsOrProcesses(self):
        for num, process in enumerate(self.parserProcesses.copy()):
            with self.processesLocker:
                self.parserProcesses.pop(num)
                self.parserDicts.pop(num)
                process.terminate()
            self.enableParserModeChanging()
        for num, thread in enumerate(self.parserThreads.copy()):
            with self.threadsLocker:
                self.parserDicts.pop(num)
                self.parserThreads.pop(num)
            self.enableParserModeChanging()


    @sendDataToLogger(operationType='user')
    def deleteCalculation(self):
        self.stopStepChanging()
        self.__calculations.pop(self.calculationFolder, None)
        if self.__calculations:
            folderToDelete = self.calculationFolder
            self.calculationFolder = list(self.__calculations.keys())[-1]
            self.__openGlWindow.loadCalculationInfo(self.__calculations[self.calculationFolder])
            self.StepSlider.setMaximum(self.__calculations[self.calculationFolder]['STEPS'] - 1)
            self.addMessage(f'Changed to {self.calculationFolder}.\n')
            self.AddedCalculations.setCurrentText(self.calculationFolder)
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(folderToDelete)
            self.AddedCalculations.removeItem(index)
        else:
            self.calculationFolder = None
            self.__openGlWindow.withoutCalculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setCurrentText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__openGlWindow._step = 0
        self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')

    @sendDataToLogger(operationType='user')
    def changeActiveCalculation(self, *args):
        self.stopStepChanging()
        newCalculationFolder = self.AddedCalculations.currentText()
        if newCalculationFolder != self.calculationFolder:
            self.calculationFolder = newCalculationFolder
            self.__openGlWindow.loadCalculationInfo(self.__calculations[self.calculationFolder])
            self.StepSlider.setMaximum(self.__calculations[self.calculationFolder]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__openGlWindow._step = 0
            self.StepLabel.setText(f'Step:\t{self.__openGlWindow._step}\tfrom\t{self.StepSlider.maximum()}')
            self.addMessage(f'Changed to {self.calculationFolder}.\n')

    @sendDataToLogger(operationType='user')
    def processingStart(self):
        self.calculationFolder = self.AddedCalculations.currentText() if self.AddedCalculations.count() else self.calculationFolder
        if self.__calculations.get(self.calculationFolder, None) is not None:
            self.stopAllThreadsOrProcesses()
            self.__processingWindow = VRProcessing(self.__app, self.__settings, self, self.getLogger(),
                                                   self.__openGlWindow, self.__calculations[self.calculationFolder], self.calculationFolder,
                                                   self.ADelete_coordinates_after_leave_cell.isChecked())
            self.__processingWindow.show()

    @sendDataToLogger
    def destroyProcessingWindow(self):
        self.__processingWindow = None

    @sendDataToLogger(operationType='user')
    def oszicarWindow(self):
        self.stopAllThreadsOrProcesses()
        self.__oszicarWindow = VROszicar(self.DirectoryPath.text(), self.__app, self.__settings, self, self.__openGlWindow, self.__logger)
        self.__oszicarWindow.show()

    @sendDataToLogger(operationType='user')
    def aboutTheProgram(self):
        message = '''VaspReader is a program firstly for processing and visualizing the results of VASP calculations. \
Have additional modes for simplify your life as more as it possible. \
It was developed at the end of 2021 and has undergone many changes described in other features of the help menu.\n'''
        self.addMessage(message, operation="Wrote about the program", operationType='user')

    @sendDataToLogger(operationType='user')
    def aboutTheWindow(self):
        message = '''Main VaspReader windows consists of control panel with the ability to add and delete calculations, \
processing them and use some additional modes such as work with supercomputer, parsing OSZICAR files, reading and work \
with POSCAR files and some others functions and visualizing of calculations window with changeable settings, such as \
lightning, background color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or \
mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, z - to move camera left, \
x - right, u - up, j - down, Backspace - return model to the first position, use arrows to rotate the model.\n'''
        self.addMessage(message, operation="Wrote about the visual window", operationType='user')

    @sendDataToLogger(operationType='user')
    def lattestUpdate(self):
        message = '''\u262D ver. 3.0.0: \u262D\n\u2705 Global update:\n1. VaspReader, consisting of several windows, \
has been redesigned into one main window with a settings menu before processing. It consists of many useful features \
such as: parsing calculation, configuration state loading/saving, loading/saving from/to json parsed calculations and \
others. You can find the entire list of options using the change history option.\n2. The position of the main window \
is now saved when the window is closed and after starting the program it will be in the saved position.\n3. Created \
two window themes: white and black. The theme is also saved when the window is closed.\n4. Added two functions: view \
model cell and axes.\n5. The position of the light can now be set by 8 edges of the cube.\n6. Added a convenient \
option to change the background.\n7. In the latest version, an orthogonal view of the model with the mode of selecting \
atoms has been added.\n8. NEW PERFECT FEATURE: The camera can be moved in all directions. You can find the binding \
keys in the visual description of the window.\n9. The bonds calculation function now activates the bonds editing \
window with 3 modes: all bonds, selected bonds and the drawing trajectory tab. A description of these options can be \
found in the update history.\n10. Reworked windows OSZICAR, POSCAR. The new graphical interface for these windows \
allows, for example, checking curves from an OSZICAR file or drawing POSCAR/CONTCAR files in the visual window.\n'''
        self.addMessage(message, operation="Wrote latest update info", operationType='user')

    @sendDataToLogger(operationType='user')
    def changesHistory(self):
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previousFile:
            message = previousFile.read()
            self.addMessage(f'{message}\n', operation="Wrote previous changes", operationType='user')
