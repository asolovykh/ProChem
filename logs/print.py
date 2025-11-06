import os
import logging
from visual.control import ControlWindow
from visual.visual import VisualWindow
from gui.print import Ui_Print, QMainWindow
logger = logging.getLogger(__name__)


class PrintWindow(Ui_Print, QMainWindow):
    def __init__(self, settings, project_directory):
        super(PrintWindow, self).__init__()
        self.__settings = settings
        self.__project_directory = project_directory
        self.__control_window = None
        self.__visual_window = None
        self.setupUi(self)
        logger.info(f"PrintUI setuped")
        
        self.__location = self.__settings.get_new_window_location('print')
        if self.__location is not None:
            self.move(self.__location[0], self.__location[1])
            logger.info(f"Print window positioned")
        self.awake_control_window()
        self.awake_visual_window()
        self.show()

    def get_settings(self):
        return self.__settings
    
    def get_visual_window(self):
        return self.__visual_window

    def get_control_window(self):
        return self.__control_window

    def get_project_dir(self):
        return self.__project_directory

    def link_elements_with_functions(self):
        pass
    
    def add_message(self, message): 
        self.Logger.append(message)
        logger.info(f'{message} added to print window')

    def closeEvent(self, event):
        self.__settings.set_new_window_location(self.pos().toTuple(), 'print')
        if self.__control_window.closed and self.__visual_window.closed:
            event.accept()
            logger.info(f"Print window closed")
            self.__settings.save_settings()
            logger.info(f"Settings saved")
        else:
            event.ignore()

    def awake_control_window(self):
        self.__control_window = ControlWindow(self.get_settings(), self)
        self.__control_window.show()
        logger.info(f"Control window awaked")

    def awake_visual_window(self):
        self.__visual_window = VisualWindow(self.get_settings(), self.get_visual_window(), self)
        self.__control_window.link_with_visual_window(self.get_visual_window())
        self.__visual_window.show()
        logger.info(f"Visual window awaked")
