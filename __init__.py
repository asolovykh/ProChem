import sys
from Logs.VRLogger import VRLogger
from Settings.VRSettings import VRSettings
from PySide6.QtWidgets import QApplication
from Logs.VRPrint import VRPrintWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    logger = VRLogger()
    settingsObject = VRSettings(logger).loadSettings()
    printWindow = VRPrintWindow(app, settingsObject, logger)
    printWindow.show()
    settingsObject.saveSettings(logger)
    sys.exit(0)
