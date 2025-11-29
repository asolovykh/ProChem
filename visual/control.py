"""Control window class"""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import codecs
import time
import logging
from multiprocessing import Process, Lock as MLock, cpu_count, Manager
from threading import Thread, Lock as TLock
from parsers.vasp import Parser as VASPparser
from vasp.processing import VRProcessing
from vasp.oszicar import VROszicar
from gui.control import Ui_Control, QMainWindow
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QColorDialog, QFileDialog

logger = logging.getLogger(__name__)

__all__ = ["ControlWindow"]


class ControlWindow(Ui_Control, QMainWindow):
    __cpu_count = cpu_count()
    
    def __init__(self, settings, print_window_object):
        super(ControlWindow, self).__init__()
        self.__settings = settings
        self.__print_window = print_window_object
        self.closed = False
        self.__project_directory = self.__print_window.get_project_dir()
        self.setupUi(self)
        logger.info(f"ControlUI setuped")
        self.link_elements_with_functions()
        logger.info(f"ControlUI elements linked with functions")
        
        self.__location = self.__settings.get_new_window_location('control')
        if self.__location is not None:
            self.move(self.__location[0], self.__location[1])
            logger.info(f"Control window positioned")

        self.__calculation_id = 1
        self.__calculations = dict()
        
        self.__parser_threads, self.__parser_processes, self.__parser_objs = [], [], []
        self.__threads_locker, self.__processes_locker = TLock(), MLock()
        self.__is_threading_mode = True
        if self.__cpu_count > 4:
            self.AThreading.setEnabled(True)
            self.AMultiprocessing.setEnabled(True)
            logger.info(f"Device has {self.__cpu_count} cores. Multiprocessing mode enabled")

        self.__visual_window = None
        self.__processing_window = None
        self.__oszicar_window = None
        
        self._window_closed = False
        self.__parser_check_thread = Thread(target=self.check_parsers, daemon=True)
        self.__parser_check_thread.start()
        self.show()
        logger.info(f"Control window initialized")

    def link_with_visual_window(self, window_object):
        self.__visual_window = window_object
        self.__visual_window.load_calculation_info(self.__calculations)
        logger.info(f"Control window linked with Visual window")

    def link_elements_with_functions(self):
        self.ALoad_Calculation.triggered.connect(self.load_calculation_files)
        self.ABackground.triggered.connect(self.background_color_change)
        self.TreeViewAddCalculation.triggered.connect(self.load_calculation_files)
        self.AAbout_the_program.triggered.connect(self.about_the_program)
        self.AAbout_window.triggered.connect(self.about_the_window)
        self.ALatest_update.triggered.connect(self.lattest_update)
        self.AChanges_history.triggered.connect(self.changes_history)
        self.AExit.triggered.connect(self.closeEvent)
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
        self.VASP_Processing.triggered.connect(self.processing_start)
        self.VASP_OSZICAR.triggered.connect(self.oszicar_window)
        self.AThreading.toggled.connect(self.set_threading)
        self.AMultiprocessing.toggled.connect(self.set_multiprocessing)
        logger.info(f"Control window elements linked with functions")

    def get_print_window(self):
        return self.__print_window

    def get_visual_window(self):
        return self.__visual_window

    def get_processing_window(self):
        return self.__processing_window

    def get_oszicar_window(self):
        return self.__oszicar_window

    def get_settings(self):
        return self.__settings

    def set_multiprocessing(self, checked):
        self.AThreading.setChecked(not checked)
        self.AMultiprocessing.setChecked(checked)
        self.__is_threading_mode = not checked
        logger.info(f"Multiprocessing mode set to {not self.__is_threading_mode}")

    def set_threading(self, checked):
        self.AThreading.setChecked(checked)
        self.AMultiprocessing.setChecked(not checked)
        self.__is_threading_mode = checked
        logger.info(f"Threading mode set to {self.__is_threading_mode}")

    def block_parser_mode_changing(self):
        self.AThreading.setEnabled(False)
        self.AMultiprocessing.setEnabled(False)
        logger.info(f"Parser mode changing blocked")

    def enable_parser_mode_changing(self):
        self.AThreading.setEnabled(True)
        self.AMultiprocessing.setEnabled(True)
        logger.info(f"Parser mode changing enabled")

    def to_first_step(self):
        self.__visual_window._step = 0
        self.StepSlider.setSliderPosition(0)
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
        logger.info(f"Step changed to 0")

    def to_last_step(self):
        self.__visual_window._step = self.__calculations[self.calculation_folder]['STEPS'] - 1
        self.StepSlider.setSliderPosition(self.__calculations[self.calculation_folder]['STEPS'] - 1)
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
        logger.info(f"Step changed to last step")

    def backward_move(self):
        self.__visual_window.back_step = True
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def forward_move(self):
        self.__visual_window.forward_step = True
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def stop_step_changing(self):
        self.__visual_window.back_step = False
        self.__visual_window.forward_step = False

    def load_calculation_files(self):
        file_names, filter = QFileDialog.getOpenFileNames(
            self,
            "Choose files for parsing",
            self.__settings.get_control_params('browse_folder_path'),
            "All Files (*);;VASP XML (*.xml)" # File filters
        )
        if file_names:
            self.__settings.set_control_params(os.path.dirname(file_names[0]), 'browse_folder_path')
            for file_name in file_names:
                self.add_calculation(file_name)

        #logger.info(f"Calculation directory chosen")

    def closeEvent(self, event=QCloseEvent):
        self.__settings.set_new_window_location(self.pos().toTuple(), 'control')
        self.closed = True
        if not self.__visual_window.closed:
            self.__visual_window.close()
        self.__print_window.close()
        event.accept()

    def keyboard_select(self, checked, *args):
        self.AKeyboard.setChecked(checked)
        self.AMouse_keyboard.setChecked(not checked)
        self.__settings.set_visual_params(checked, 'only_keyboard_selection')
        logger.info(f"Keyboard selection set to {checked}")

    def mouse_and_keyboard_select(self, checked, *args):
        self.AKeyboard.setChecked(not checked)
        self.AMouse_keyboard.setChecked(checked)
        self.__settings.set_visual_params(not checked, 'only_keyboard_selection')
        self.get_print_window().add_message('Changed to mouse+keyboard mode.' if checked else 'Changed to keyboard mode.')
        logger.info(f"Mouse+keyboard mode set to {checked}")

    def perspective_chosen(self, checked, *args):
        self.APerspective.setChecked(checked)
        self.AOrthographic.setChecked(not checked)
        self.__settings.set_visual_params(checked, 'view', 'perspective')
        logger.info(f"Perspective mode set to {checked}")

    def orthographic_chosen(self, checked, *args):
        self.APerspective.setChecked(not checked)
        self.AOrthographic.setChecked(checked)
        self.__settings.set_visual_params(not checked, 'view', 'perspective')
        self.get_print_window().add_message('Changed to orthographic view' if checked else 'Changed to perspective view')
        logger.info(f"Orthographic mode set to {checked}")

    def background_color_change(self):
        color = tuple([el[i] / 255 for col in QColorDialog().getColor().toTuple()])
        self.__settings.set_scene_params(color, 'background', 'color')
        self.__settings.set_scene_params(color, 'fog', 'color')
        self.get_print_window().add_message(f'Background color changed to {color}')
        logger.info(f"Background color changed to {color}")

    def calculation_step_change(self):
        self.stop_step_changing()
        self.__visual_window._step = self.StepSlider.sliderPosition()
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def speed_change(self):
        self.__settings.set_visual_params(self.SpeedSlider.sliderPosition(), 'slider_speed')

    def add_calculation(self, file_path: str):
        self.stop_step_changing()
        for calc_id in self.__calculations:
            for calc in self.__calculations[calc_id].get('calculations', []):
                if os.path.join(calc.directory, calc.name) == file_path:
                    logger.info(f"Calculation {file_path} already added")
                    return

        parser = VASPparser(file_path)
        if self.__is_threading_mode:
            self.__parser_objs.append(parser)
            self.__parser_threads.append(Thread(target=parser.read, args=(), daemon=True))
            self.__parser_threads[-1].start()
        else:
            self.__parser_objs.append(parser)
            self.__parser_processes.append(Process(target=parser.read, args=(), daemon=True))
            self.__parser_processes[-1].start()
        self.block_parser_mode_changing()
        logger.info(f"Calculation {file_path} parsing in " + "threading" if self.__is_threading_mode else "multiprocessing" + " mode")

    def check_parsers(self):
        while True:
            if self.__is_threading_mode and self.__parser_threads:
                for num, thread in enumerate(self.__parser_threads.copy()):
                    if not thread.is_alive():
                        with self.__threads_locker:
                            self.process_add_action(self.__parser_objs.pop(num))
                            self.__parser_threads.pop(num)
                if not self.__parser_threads:
                    self.enable_parser_mode_changing()
            elif not self.__is_threading_mode and self.__parser_processes:
                for num, process in enumerate(self.__parser_processes.copy()):
                    if not process.is_alive():
                        with self.__processes_locker:
                            self.process_add_action(dict(self.__parser_objs.pop(num)))
                            self.__parser_processes.pop(num)
                if not self.__parser_processes:
                    self.enable_parser_mode_changing()
            time.sleep(0.2)

    def process_add_action(self, parser):
        if parser.get_calculation().errors.exist:
            self.get_print_window().add_message(parser.get_calculation().errors.message)
            logger.error(f"Error in parsing {parser.get_calculation().directory}: {parser.get_calculation().errors.message}")
        else:
            id = -1
            for calc_id in range(self.__calculation_id):
                if calc_id not in self.__calculations:
                    id = calc_id
                    self.__calculations[id] = {'visible': True, 'calculations': []}
                    self.__calculations[id]['calculations'] = [parser.get_calculation()]
                    break
            else:
                self.__calculation_id += 1
                id = self.__calculation_id
                self.__calculations[id] = {'visible': True, 'calculations': []}
                self.__calculations[id]['calculations'] = [parser.get_calculation()]
            
            self.TreeModel.append_data([([id, 'V', parser.get_calculation().directory, parser.get_calculation().calculation_type], 
                                         [(['', '', parser.get_calculation().name, ''], None)])], self.TreeModel.root_item)
            self.TreeView.expandAll()
            self.get_print_window().add_message(f'File {self.__calculations[id]["calculations"][-1].name} appended.\n')
            self.StepSlider.setMaximum(self.__calculations[id]['calculations'][-1].positions.shape[0] - 1)
            self.StepSlider.setValue(0)
            self.__visual_window._step = 0
            self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
            logger.info(f"Calculation {parser.get_calculation().name} parsed")

    def stop_all_threads_or_processes(self):
        for num, process in enumerate(self.__parser_processes.copy()):
            with self.__processes_locker:
                self.__parser_processes.pop(num)
                self.__parser_objs.pop(num)
                process.terminate()
            self.enable_parser_mode_changing()
        for num, thread in enumerate(self.__parser_threads.copy()):
            with self.__threads_locker:
                self.__parser_objs.pop(num)
                self.__parser_threads.pop(num)
            self.enable_parser_mode_changing()

    def delete_calculation(self):
        self.stop_step_changing()
        self.__calculations.pop(self.calculation_folder, None)
        logger.info(f"Calculation {self.calculation_folder} deleted")
        if self.__calculations:
            folder_to_delete = self.calculation_folder
            self.calculation_folder = list(self.__calculations.keys())[-1]
            self.__visual_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')
            self.AddedCalculations.setCurrentText(self.calculation_folder)
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(folder_to_delete)
            self.AddedCalculations.removeItem(index)
        else:
            self.calculation_folder = None
            self.__visual_window.without_calculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setCurrentText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__visual_window._step = 0
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def change_active_calculation(self, *args):
        self.stop_step_changing()
        new_calculation_folder = self.AddedCalculations.currentText()
        if new_calculation_folder != self.calculation_folder:
            self.calculation_folder = new_calculation_folder
            self.__visual_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__visual_window._step = 0
            self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')
            logger.info(f"Changed to {self.calculation_folder}")

    def processing_start(self):
        self.calculation_folder = self.AddedCalculations.currentText() if self.AddedCalculations.count() else self.calculation_folder
        if self.__calculations.get(self.calculation_folder, None) is not None:
            self.stop_all_threads_or_processes()
            self.__processing_window = Processing(self.__settings, self, self.__print_window,
                                                   self.__visual_window, self.__calculations[self.calculation_folder], self.calculation_folder,
                                                   self.ADelete_coordinates_after_leave_cell.isChecked())
            self.__processing_window.show()

    def destroy_processing_window(self):
        self.__processing_window = None

    def oszicar_window(self):
        self.stop_all_threads_or_processes()
        self.__oszicar_window = Oszicar(self.DirectoryPath.text(), self.__settings, self, self.__visual_window, self.__print_window)
        self.__oszicar_window.show()

    def about_the_program(self):
        message = '''PROCHEM is a program for processing and visualization the results of quantum chemistry packages' calculations. \
Have additional modes for simplify your life as more as it possible. \
It was developed at the end of 2021 and has undergone many changes and rebrending described in other features of the help menu.\n'''
        self.get_print_window().add_message(message)
        logger.info(f"About the program function called")

    def about_the_window(self):
        message = '''Main PROCHEM windows consists of control panel with the ability to add and delete calculations, \
processing them and use some additional modes such as work with supercomputer, parsing OSZICAR files, reading and work \
with POSCAR files and some others functions and visualizing of calculations window with changeable settings, such as \
lightning, background color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or \
mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, z - to move camera left, \
x - right, u - up, j - down, Backspace - return model to the first position, use arrows to rotate the model.\n'''
        self.get_print_window().add_message(message)
        logger.info(f"About the window function called")

    def lattest_update(self):
        message = '''\u262D ver. 1.0: \u262D\n\u2705 Global update:\n1. PROCHEM, consisting of several windows, \
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
        logger.info(f"Latest update function called")

    def changes_history(self):
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previous_changes_file:
            message = previous_changes_file.read()
            self.get_print_window().add_message(f'{message}\n')
        logger.info(f"Changes history function called")
