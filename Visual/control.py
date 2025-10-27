import os
import codecs
import time
import logging
from multiprocessing import Process, Lock as MLock, cpu_count, Manager
from threading import Thread, Lock as TLock
from Processing.VRMD import VRMD #, QEMD
# from Processing.VRProcessing import VRProcessing
# from Processing.VROszicar import VROszicar
from Gui.VRVisualGUI import Ui_VRVisual, QMainWindow
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QColorDialog, QFileDialog
logger = logging.getLogger(__name__)


class VRVisualWindow(Ui_VRVisual, QMainWindow):
    __cpu_count = cpu_count()
    
    def __init__(self, settings, print_window_object):
        super(VRVisualWindow, self).__init__()
        self.__settings = settings
        self.__print_window = print_window_object
        self.__project_directory = self.__print_window.get_project_dir()
        self.setupUi(self)
        logger.info(f"VisualUI setuped")
        self.link_elements_with_functions()
        logger.info(f"VisualUI elements linked with functions")
        
        self.__location = self.__settings.get_new_window_location('visual')
        if self.__location is not None:
            self.move(self.__location[0], self.__location[1])
            logger.info(f"Visual window positioned")

        self.calculation_folder = None
        self.__calculations = dict()
        
        self.__parser_threads, self.__parser_processes, self.__parser_dicts = [], [], []
        self.__threads_locker, self.__processes_locker = TLock(), MLock()
        self.__is_threading_mode = True
        if self.__cpu_count > 4:
            self.AThreading.setEnabled(True)
            self.AMultiprocessing.setEnabled(True)
            logger.info(f"Device has {self.__cpu_count} cores. Multiprocessing mode enabled")

        self.__opengl_window = None
        self.__processing_window = None
        self.__oszicar_window = None
        
        self._window_closed = False
        self.__parser_check_thread = Thread(target=self.check_parsers, daemon=True)
        self.__parser_check_thread.start()
        self.show()
        logger.info(f"Visual window initialized")

    def link_with_opengl_window(self, window_object):
        self.__opengl_window = window_object

    def link_elements_with_functions(self):
        self.AOpen_calculation.triggered.connect(self.open_calculation_folder)
        self.ABackground.triggered.connect(self.background_color_change)
        self.BrowseButton.clicked.connect(self.open_calculation_folder)
        self.AAbout_the_program.triggered.connect(self.about_the_program)
        self.AAbout_window.triggered.connect(self.about_the_window)
        self.ALatest_update.triggered.connect(self.lattest_update)
        self.AChanges_history.triggered.connect(self.changes_history)
        self.AExit.triggered.connect(self.closeEvent)
        self.CalculationAddButton.clicked.connect(self.add_calculation)
        self.AddedCalculations.activated.connect(self.change_active_calculation)
        self.DeleteCalculationButton.clicked.connect(self.delete_calculation)
        self.StepSlider.actionTriggered.connect(self.calculation_step_change)
        self.SpeedSlider.actionTriggered.connect(self.speed_change)
        self.APerspective.toggled.connect(self.perspective_chosen)
        self.AOrthographic.toggled.connect(self.orthographic_chosen)
        self.AKeyboard.toggled.connect(self.keyboard_select)
        self.AMouse_keyboard.toggled.connect(self.mouse_and_keyboard_select)
        self.MoveBack.clicked.connect(self.backward_move)
        self.MoveForward.clicked.connect(self.forward_move)
        self.ToFirstStep.clicked.connect(self.to_first_step)
        self.ToLastStep.clicked.connect(self.to_last_step)
        # self.VASP_Processing.triggered.connect(self.processing_start)
        # self.VASP_OSZICAR.triggered.connect(self.oszicar_window)
        self.AThreading.toggled.connect(self.settings_threading)
        self.AMultiprocessing.toggled.connect(self.settings_multiprocessing)

    def get_print_window(self):
        return self.__print_window

    def get_opengl_window(self):
        return self.__opengl_window

    def get_processing_window(self):
        return self.__processing_window

    def get_oszicar_window(self):
        return self.__oszicar_window

    def get_settings(self):
        return self.__settings

    def settings_multiprocessing(self, checked):
        if checked:
            self.AThreading.setChecked(False)
            self.AMultiprocessing.setChecked(True)
        else:
            self.AThreading.setChecked(True)
            self.AMultiprocessing.setChecked(False)
        self.__is_threading_mode = not checked

    def settings_threading(self, checked):
        if checked:
            self.AThreading.setChecked(True)
            self.AMultiprocessing.setChecked(False)
        else:
            self.AThreading.setChecked(False)
            self.AMultiprocessing.setChecked(True)
        self.__is_threading_mode = checked

    def block_parser_mode_changing(self):
        self.AThreading.setEnabled(False)
        self.AMultiprocessing.setEnabled(False)

    def enable_parser_mode_changing(self):
        self.AThreading.setEnabled(True)
        self.AMultiprocessing.setEnabled(True)

    def to_first_step(self):
        self.__opengl_window._step = 0
        self.StepSlider.setSliderPosition(0)
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def to_last_step(self):
        self.__opengl_window._step = self.__calculations[self.calculation_folder]['STEPS'] - 1
        self.StepSlider.setSliderPosition(self.__calculations[self.calculation_folder]['STEPS'] - 1)
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def backward_move(self):
        self.__opengl_window.back_step = True
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def forward_move(self):
        self.__opengl_window.forward_step = True
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def stop_step_changing(self):
        self.__opengl_window.back_step = False
        self.__opengl_window.forward_step = False

    def open_calculation_folder(self):
        self.DirectoryPath.setText(QFileDialog.getExistingDirectory(None, caption="Choose directory to parse"))

    def closeEvent(self, event=QCloseEvent):
        self.__settings.set_new_window_location(self.pos().toTuple(), 'visual')
        self.__print_window.close()
        self.__opengl_window._parent_window_closed = True
        self.__print_window._visual_window_closed = True
        event.accept()

    def keyboard_select(self, checked, *args):
        if checked:
            self.AKeyboard.setChecked(True)
            self.AMouse_keyboard.setChecked(False)
            self.__settings.set_visual_params(True, 'only_keyboard_selection')
        else:
            self.AKeyboard.setChecked(False)
            self.AMouse_keyboard.setChecked(True)
            self.__settings.set_visual_params(False, 'only_keyboard_selection')

    def mouse_and_keyboard_select(self, checked, *args):
        if checked:
            self.AKeyboard.setChecked(False)
            self.AMouse_keyboard.setChecked(True)
            self.__settings.set_visual_params(False, 'only_keyboard_selection')
            self.get_print_window().add_message('Changed to mouse+keyboard mode.')
        else:
            self.AKeyboard.setChecked(True)
            self.AMouse_keyboard.setChecked(False)
            self.__settings.set_visual_params(True, 'only_keyboard_selection')
            self.get_print_window().add_message('Changed to keyboard mode.')

    def perspective_chosen(self, checked, *args):
        if checked:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__settings.set_visual_params(True, 'view', 'perspective')
        else:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__settings.set_visual_params(False, 'view', 'perspective')

    def orthographic_chosen(self, checked, *args):
        if checked:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__settings.set_visual_params(False, 'view', 'perspective')
            self.get_print_window().add_message('Changed to orthographic view')
        else:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__settings.set_visual_params(True, 'view', 'perspective')
            self.get_print_window().add_message('Changed to perspective view')

    def background_color_change(self):
        color = tuple([el[i] / 255 for col in QColorDialog().getColor().toTuple()])
        self.__settings.set_scene_params(color, 'background', 'color')
        self.__settings.set_scene_params(color, 'fog', 'color')
        self.get_print_window().add_message(f'Background color changed to {color}')

    def calculation_step_change(self):
        self.stop_step_changing()
        self.__opengl_window._step = self.StepSlider.sliderPosition()
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def speed_change(self):
        self.__settings.set_visual_params(self.SpeedSlider.sliderPosition(), 'slider_speed')

    def add_calculation(self):
        self.stop_step_changing()
        self.calculation_folder = self.DirectoryPath.text()
        if self.calculation_folder and self.calculation_folder not in self.__calculations:
            if self.__is_threading_mode:
                self.__parser_dicts.append(dict())
                self.__parser_threads.append(Thread(target=VRMD, args=(self.calculation_folder, self.__parser_dicts[-1],), daemon=True))
                self.__parser_threads[-1].start()
            else:
                self.__parser_dicts.append(Manager().dict())
                self.__parser_processes.append(Process(target=VRMD, args=(self.calculation_folder, self.__parser_dicts[-1],), daemon=True))
                self.__parser_processes[-1].start()
            self.block_parser_mode_changing()

    def check_parsers(self):
        while True:
            if self.__is_threading_mode and self.__parser_threads:
                for num, thread in enumerate(self.__parser_threads.copy()):
                    if not thread.is_alive():
                        with self.__threads_locker:
                            self.process_add_action(self.__parser_dicts.pop(num))
                            self.__parser_threads.pop(num)
                if not self.__parser_threads:
                    self.enable_parser_mode_changing()
            elif not self.__is_threading_mode and self.__parser_processes:
                for num, process in enumerate(self.__parser_processes.copy()):
                    if not process.is_alive():
                        with self.__processes_locker:
                            self.process_add_action(dict(self.__parser_dicts.pop(num)))
                            self.__parser_processes.pop(num)
                if not self.__parser_processes:
                    self.enable_parser_mode_changing()
            time.sleep(0.1)

    def process_add_action(self, parser_parameters):
        directory = parser_parameters['DIRECTORY']
        if parser_parameters['BREAKER']:
            self.get_print_window().add_message(parser_parameters['MESSAGE'])
        else:
            self.__calculations[directory] = parser_parameters
            self.__opengl_window.load_calculation_info(self.__calculations[directory])
            self.get_print_window().add_message(f'Chosen {directory} appended.\n')
            self.AddedCalculations.addItem(directory)
            self.AddedCalculations.setCurrentText(directory)
            self.StepSlider.setMaximum(self.__calculations[directory]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__opengl_window._step = 0
            self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def stop_all_threads_or_processes(self):
        for num, process in enumerate(self.__parser_processes.copy()):
            with self.__processes_locker:
                self.__parser_processes.pop(num)
                self.__parser_dicts.pop(num)
                process.terminate()
            self.enable_parser_mode_changing()
        for num, thread in enumerate(self.__parser_threads.copy()):
            with self.__threads_locker:
                self.__parser_dicts.pop(num)
                self.__parser_threads.pop(num)
            self.enable_parser_mode_changing()

    def delete_calculation(self):
        self.stop_step_changing()
        self.__calculations.pop(self.calculation_folder, None)
        if self.__calculations:
            folder_to_delete = self.calculation_folder
            self.calculation_folder = list(self.__calculations.keys())[-1]
            self.__opengl_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')
            self.AddedCalculations.setCurrentText(self.calculation_folder)
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(folder_to_delete)
            self.AddedCalculations.removeItem(index)
        else:
            self.calculation_folder = None
            self.__opengl_window.without_calculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setCurrentText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__opengl_window._step = 0
        self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def change_active_calculation(self, *args):
        self.stop_step_changing()
        new_calculation_folder = self.AddedCalculations.currentText()
        if new_calculation_folder != self.calculation_folder:
            self.calculation_folder = new_calculation_folder
            self.__opengl_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__opengl_window._step = 0
            self.StepLabel.setText(f'Step:\t{self.__opengl_window._step}\tfrom\t{self.StepSlider.maximum()}')
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')

    #def processing_start(self):
    #    self.calculation_folder = self.AddedCalculations.currentText() if self.AddedCalculations.count() else self.calculation_folder
    #    if self.__calculations.get(self.calculation_folder, None) is not None:
    #        self.stop_all_threads_or_processes()
    #        self.__processing_window = VRProcessing(self.__settings, self, self.__print_window,
    #                                               self.__opengl_window, self.__calculations[self.calculation_folder], self.calculation_folder,
    #                                               self.ADelete_coordinates_after_leave_cell.isChecked())
    #        self.__processing_window.show()

    #def destroy_processing_window(self):
    #    self.__processing_window = None

    #def oszicar_window(self):
    #    self.stop_all_threads_or_processes()
    #    self.__oszicar_window = VROszicar(self.DirectoryPath.text(), self.__settings, self, self.__opengl_window, self.__print_window)
    #    self.__oszicar_window.show()

    def about_the_program(self):
        message = '''VaspReader is a program firstly for processing and visualizing the results of VASP calculations. \
Have additional modes for simplify your life as more as it possible. \
It was developed at the end of 2021 and has undergone many changes described in other features of the help menu.\n'''
        self.get_print_window().add_message(message)

    def about_the_window(self):
        message = '''Main VaspReader windows consists of control panel with the ability to add and delete calculations, \
processing them and use some additional modes such as work with supercomputer, parsing OSZICAR files, reading and work \
with POSCAR files and some others functions and visualizing of calculations window with changeable settings, such as \
lightning, background color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or \
mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, z - to move camera left, \
x - right, u - up, j - down, Backspace - return model to the first position, use arrows to rotate the model.\n'''
        self.get_print_window().add_message(message)

    def lattest_update(self):
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
        self.get_print_window.add_message(message)

    def changes_history(self):
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previous_changes_file:
            message = previous_changes_file.read()
            self.get_print_window().add_message(f'{message}\n')
