import os
import codecs
from Processing.VRMD import VRMD, QEMD
from Processing.VRProcessing import VRProcessing
from Processing.VROszicar import VROszicar
from Gui.VRVisualGUI import Ui_VRVisual, QColorDialog, QFileDialog, QMainWindow
from PySide6.QtGui import QCloseEvent
from Logs.VRLogger import sendDataToLogger


class VRVisualWindow(Ui_VRVisual, QMainWindow):
    __project_directory = os.path.abspath('')

    @sendDataToLogger
    def __init__(self, app, settings, printWindowObject):
        super(VRVisualWindow, self).__init__()
        self.__logger = printWindowObject
        self.calculationFolder = None
        self.__calculations = dict()
        self.__app = app
        self.__settings = settings
        location = self.__settings.visualWindowLocation
        self.setupUi(self)
        self.linkElementsWithFunctions()
        if location is not None:
            self.move(location[0], location[1])
        self.show()

        self.__openGlWindow = None
        self.__processingWindow = None
        self.__oszicarWindow = None
        self._stepSliderSpeed = 1
        self._backgroundColor = (0.6, 0.6, 0.6, 1.0)
        self._windowClosed = False

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
        self.MoveBack.clicked.connect(self.backwardMove)
        self.MoveForward.clicked.connect(self.forwardMove)
        self.ToFirstStep.clicked.connect(self.toFirstStep)
        self.ToLastStep.clicked.connect(self.toLastStep)
        self.AProcessing.triggered.connect(self.processingStart)
        self.AOSZICAR.triggered.connect(self.oszicarWindow)

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger(operationType='user')
    def toFirstStep(self):
        self.__openGlWindow._step = 0
        self.StepSlider.setSliderPosition(0)

    @sendDataToLogger(operationType='user')
    def toLastStep(self):
        self.__openGlWindow._step = self.__calculations[self.calculationFolder]['STEPS'] - 1
        self.StepSlider.setSliderPosition(self.__calculations[self.calculationFolder]['STEPS'] - 1)

    @sendDataToLogger(operationType='user')
    def backwardMove(self):
        self.__openGlWindow.Back_Step = True

    @sendDataToLogger(operationType='user')
    def forwardMove(self):
        self.__openGlWindow.Forward_Step = True

    def stopStepChanging(self):
        self.__openGlWindow.Back_Step = False
        self.__openGlWindow.Forward_Step = False

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
    def perspectiveChose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__openGlWindow.is_perspective = True
            self.addMessage('Changed to perspective view')
        else:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__openGlWindow.is_perspective = False
            self.addMessage('Changed to orthographic view')

    @sendDataToLogger(operationType='user')
    def orthographicChose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__openGlWindow.is_perspective = False
            self.addMessage('Changed to orthographic view')
        else:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__openGlWindow.is_perspective = True
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

    def speedChange(self):
        self._stepSliderSpeed = self.SpeedSlider.sliderPosition()
        self.__openGlWindow._speed = self._stepSliderSpeed

    @sendDataToLogger(operationType='user')
    def addCalculation(self):
        self.stopStepChanging()
        self.calculationFolder = self.DirectoryPath.text()
        if self.calculationFolder not in self.__calculations:
            parserObj = VRMD(self.calculationFolder, self.getLogger())
            self.__calculations[self.calculationFolder] = parserObj._parser_parameters
            if parserObj.breaker:
                self.__calculations.pop(self.calculationFolder)
                parserObj = QEMD(self.calculationFolder, self.getLogger())
                self.__calculations[self.calculationFolder] = parserObj._parser_parameters
            if not parserObj.breaker:
                self.__openGlWindow.loadCalculationInfo(self.__calculations[self.calculationFolder])
                self.addMessage(f'Chosen {self.calculationFolder} appended.\n')
                self.AddedCalculations.addItem(self.calculationFolder)
                self.AddedCalculations.setPlaceholderText(self.calculationFolder)
                self.StepSlider.setMaximum(self.__calculations[self.calculationFolder]['STEPS'] - 1)
                self.StepSlider.setValue(0)
                self.__openGlWindow._step = 0
            else:
                self.__calculations.pop(self.calculationFolder)

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
            self.AddedCalculations.setPlaceholderText(self.calculationFolder)
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(folderToDelete)
            self.AddedCalculations.removeItem(index)
        else:
            self.calculationFolder = None
            self.__openGlWindow.withoutCalculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setPlaceholderText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__openGlWindow._step = 0

    @sendDataToLogger(operationType='user')
    def changeActiveCalculation(self):
        self.stopStepChanging()
        newCalculationFolder = self.AddedCalculations.currentText()
        if newCalculationFolder != self.calculationFolder:
            self.calculationFolder = newCalculationFolder
            self.__openGlWindow.loadCalculationInfo(self.__calculations[self.calculationFolder])
            self.StepSlider.setMaximum(self.__calculations[self.calculationFolder]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__openGlWindow._step = 0
            self.addMessage(f'Changed to {self.calculationFolder}.\n')

    @sendDataToLogger(operationType='user')
    def processingStart(self):
        if self.__calculations[self.calculationFolder]['STEPS']:
            self.__processingWindow = VRProcessing(self.__app, self.__settings, self, self.getLogger(),
                                                   self.__openGlWindow, self.__calculations[self.calculationFolder], self.calculationFolder,
                                                   self.ADelete_coordinates_after_leave_cell.isChecked())
            self.__processingWindow.show()

    @sendDataToLogger
    def destroyProcessingWindow(self):
        self.__processingWindow = None

    @sendDataToLogger(operationType='user')
    def oszicarWindow(self):
        self.__oszicarWindow = VROszicar(self.calculationFolder, self.__app, self.__settings, self, self.__openGlWindow, self.__logger)
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
