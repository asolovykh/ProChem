from Logs.VRLogger import sendDataToLogger
from Visual.VRVisual import VRVisualWindow
from Visual.VROpenGL import VROpenGL
from Gui.VRPrintGUI import Ui_VRPrint, QMainWindow


class VRPrintWindow(Ui_VRPrint, QMainWindow):

    @sendDataToLogger
    def __init__(self, app, settings, logger):
        super(VRPrintWindow, self).__init__()
        self.__logger = logger
        self.__app = app
        self.__visualWindow = None
        self._visualWindowClosed = False
        self.__openGlWindow = None
        self.__settings = settings
        location = self.__settings.printWindowLocation
        self.setupUi(self)
        if location is not None:
            self.move(location[0], location[1])
        self.show()
        self.awakeVisualWindow()
        self.awakeOpenGlWindow()
        self.openGlMainloop()

    def getLogger(self):
        return self.__logger

    def insertLogs(self, window, operation, operationType, result='SUCCESS', cause=None, detailedDescription=None):
        self.getLogger().insertLogs(window, operation, operationType, result, cause, detailedDescription)

    def addMessage(self, message, fromWindow, operation=None, operationType='program', result='SUCCESS', cause=None, detailedDescription=None):
        message = str(message)
        toLogger = message if operation is None else operation
        message = message.split('\n')
        for line in message:
            self.Logger.append(f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Times New Roman'; font-size:10pt; font-weight:696; color:#00e5e5; background-color:#000000\">{line}</span></p>\n")
        toLogger = toLogger.replace(r"'", r"")
        self.getLogger().insertLogs(fromWindow, toLogger, operationType, result, cause, detailedDescription)

    def linkElementsWithFunctions(self):
        pass

    @sendDataToLogger
    def closeEvent(self, event):
        self.__settings.printWindowLocation = self.pos().toTuple()
        if self._visualWindowClosed:
            event.accept()
        else:
            event.ignore()

    @sendDataToLogger
    def awakeVisualWindow(self):
        self.__visualWindow = VRVisualWindow(self.__app, self.__settings, self)
        self.__visualWindow.show()

    @sendDataToLogger
    def awakeOpenGlWindow(self):
        self.__openGlWindow = VROpenGL(self.__app, self.__settings, self.__visualWindow, self)
        self.__visualWindow.linkWithOpenGlWindow(self.__openGlWindow)

    @sendDataToLogger
    def openGlMainloop(self):
        self.__openGlWindow.mainloop()
