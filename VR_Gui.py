import sys
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QApplication
from Create_a_GUI_and_save_every_word_here..Control_and_save_every_word_here. import Ui_Control


class VRGui(QMainWindow, Ui_Control):

    def __init__(self):
        super(VRGui, self).__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VRGui()
    window.show()
    sys.exit(app.exec())
