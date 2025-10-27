import os
import json
import numpy as np
import logging
logger = logging.getLogger(__name__)


class Settings:
    def __init__(self, project_directory):
        self.__project_directory = project_directory
        self.__settings_file = os.path.join(project_directory, 'settings', 'settings.json')
        self.__set_default_settings()

    def __set_default_settings(self):
        self.__new_window_location = {
            "print": None,
            "visual": None,
            "processing": None,
            "graph": None,
            "file_sharing": None,
            "console": None,
            "chgcar": None,
            "form_poscar": None,
            "oszicar": None,
            "bonds": None
        }
        self.__scene_params = {
            'light': {
                'variables': '',
                'states': {i: False for i in range(8)},
                'positions': [[10, 10, 10], [10, 10, -10], [10, -10, 10], 
                              [10, -10, -10], [-10, 10, 10], [-10, 10, -10],
                              [-10, -10, 10], [-10, -10, -10]],
                'default': [[10, 10, 10, 0.0], [-10, -10, 10, 1.0], 
                            [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 
                            [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 
                            [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], 
                'intensities': [[0.4, 0.4, 0.4], [0.4, 0.4, 0.4], 
                                [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                'kd': [0.3, 0.3, 0.3],
                'ld': [0.7, 0.7, 0.7],
                'ka': [0.5, 0.5, 0.5],
                'ks': [0.8, 0.8, 0.8],
                'shininess': 10.0
            },
            'draw': {
                'type': ''
            },
            'view': {
                'axes': True,
                'cell_border': True,
                'perspective': True,
                'eye_position': [0.0, 0.0, 20.0]
            },
            'background': {
                'color': (0.6, 0.6, 0.6, 1.0)
            },
            'fog': {
                'color': (0.6, 0.6, 0.6, 1.0),
                'min_dist': 10,
                'max_dist': 60,
                'power': 1,
                'density': 0.05
            },
            'bond': {
                'length': 1.8,
                'radius': 0.2
            }
        }
        self.__visual_params = {
            'only_keyboard_selection': True,
            'slider_speed': 1
        }
        self.__processing_params = {
            'delete_coordinates_after_leave_cell': True
        }
        logger.info(f"Default settings initialized")

    def load_settings(self):
        try:
            with open(self.get_settings_filename(), 'r') as file:
                data = json.load(file)
            for key in list(data[1]['light']['states'].keys()):
                data[1]['light']['states'][int(key)] = data[1]['light']['states'].pop(key)
            logger.info(f"Settings json read")
            __settings_default = [self.__new_window_location, self.__scene_params,
                                  self.__visual_params, self.__processing_params]
            for indx, json_data in enumerate(data):
                Settings.check_settings_keys(__settings_default[indx], json_data)
                __settings_default[indx] = json_data
            logger.info(f"Settings loaded from {self.get_settings_filename()}")
        except FileNotFoundError:
            self.save_settings()
            logger.warning(f"Settings file not found. Default settings saved to {self.get_settings_filename()}")
        except KeyError:
            self.save_settings()
            logger.error(f"Settings file corrupted. Default settings saved to {self.get_settings_filename()}")
        return self

    @staticmethod
    def check_settings_keys(valid_dict, check_dict):
        for key in valid_dict:
            if key not in check_dict:
                raise KeyError(f"Key {key} not found in settings file.")
            if isinstance(valid_dict[key], dict):
                Settings.check_settings_keys(valid_dict[key], check_dict[key])

    def get_settings_filename(self):
        return self.__settings_file

    @staticmethod
    def __get_dict_value(dict_object, *keys):
        if len(keys) == 1:
            return dict_object[keys[0]]
        else:
            return Settings.__get_dict_value(dict_object[keys[0]], *keys[1:])

    @staticmethod
    def __set_dict_value(dict_object, value, *keys):
        if len(keys) == 1:
            dict_object[keys[0]] = value
        else:
            Settings.__set_dict_value(dict_object[keys[0]], value, *keys[1:])

    def get_new_window_location(self, *keys):
        return Settings.__get_dict_value(self.__new_window_location, *keys)

    def set_new_window_location(self, value, *keys):
        Settings.__set_dict_value(self.__new_window_location, value, *keys)

    def get_scene_params(self, *keys):
        return Settings.__get_dict_value(self.__scene_params, *keys)

    def set_scene_params(self, value, *keys):
        Settings.__set_dict_value(self.__scene_params, value, *keys)

    def get_visual_params(self, *keys):
        return Settings.__get_dict_value(self.__visual_params, *keys)

    def set_visual_params(self, value, *keys):
        Settings.__set_dict_value(self.__visual_params, value, *keys)

    def get_processing_params(self, *keys):
        return Settings.__get_dict_value(self.__processing_params, *keys)

    def set_processing_params(self, value, *keys):
        Settings.__set_dict_value(self.__processing_params, value, *keys)

    def save_settings(self):
        self.__scene_params['light']['variables'] = ''
        self.__scene_params['draw']['type'] = ''
        json_data = [self.__new_window_location, self.__scene_params, 
                     self.__visual_params, self.__processing_params]
        with open(self.get_settings_filename(), 'w') as file:
            json.dump(json_data, file)
        return self
