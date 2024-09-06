import sys
import os
from Logs.VRLogger import VRLogger
from Settings.VRSettings import VRSettings
from PySide6.QtWidgets import QApplication
from Logs.VRPrint import VRPrintWindow


if __name__ == '__main__':
    _project_dir = os.path.abspath(__file__).removesuffix('__init__.py')
    app = QApplication(sys.argv)
    logger = VRLogger(_project_dir)
    settingsObject = VRSettings(logger, _project_dir).loadSettings()
    printWindow = VRPrintWindow(app, settingsObject, logger, _project_dir)
    printWindow.show()
    settingsObject.saveSettings(logger)
    sys.exit(0)
