import sys
import argparse
import os
import logging
from settings.settings import Settings
from PySide6.QtWidgets import QApplication
from logs.print import PrintWindow


if __name__ == "__main__":
    # TODO redact README.md
    argparser = argparse.ArgumentParser(
        prog="ProChem",
        description="ProChem is a program for reading and analyzing quantum chemistry calculations.",
        epilog="Developed by A.A.Solovykh",
    )
    argparser.add_argument("-v", "--version", action="version", version="ProChem 1.0.0")
    argparser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode"
    )
    args = argparser.parse_args()

    project_dir = os.path.abspath(__file__).removesuffix("__init__.py")
    logging.basicConfig(
        filename=os.path.join(project_dir, "logs", "ProChem.log"),
        level=logging.INFO if not args.debug else logging.DEBUG,
        filemode="w",
    )
    app = QApplication(sys.argv)
    settings_object = Settings(project_dir).load_settings()
    print_window = PrintWindow(settings_object, project_dir)
    sys.exit(app.exec())
