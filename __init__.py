import sys
import os
import logging
from settings.settings import Settings
from PySide6.QtWidgets import QApplication
from logs.print import PrintWindow


if __name__ == "__main__":
    project_dir = os.path.abspath(__file__).removesuffix("__init__.py")
    logging.basicConfig(
        filename=os.path.join(project_dir, "Logs", "VR.log"), level=logging.INFO
    )
    app = QApplication(sys.argv)
    settingsObject = VRSettings(project_dir).load_settings()
    printWindow = VRPrintWindow(settingsObject, project_dir)
    app.exec()
    settingsObject.save_settings()
    sys.exit(0)
