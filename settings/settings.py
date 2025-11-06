import os
import json
import numpy as np
import logging
logger = logging.getLogger(__name__)


class Settings:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_directory):
        if not self._initialized:
            self._initialized = True
            self.__project_directory = project_directory
            self.__settings_file = os.path.join(project_directory, 'settings', 'settings.json')
            self.__set_default_settings()

    def __set_default_settings(self):
        self.__new_window_location = {
            "print": None,
            "control": None,
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
                'states': {i: False if i > 1 else True for i in range(8)},
                'positions': np.array([[10.0, 10.0, 10.0, 1.0], [10.0, 10.0, -10.0, 1.0], 
                                       [10.0, -10.0, 10.0, 1.0], [10.0, -10.0, -10.0, 1.0],
                                       [-10.0, 10.0, 10.0, 1.0], [-10.0, 10.0, -10.0, 1.0],
                                       [-10.0, -10.0, 10.0, 1.0], [-10.0, -10.0, -10.0, 1.0]]),
                'intensities': np.array([[0.8, 0.8, 0.8], [0.8, 0.8, 0.8], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
                'kd': np.array([0.3, 0.3, 0.3]),
                'ld': np.array([0.7, 0.7, 0.7]),
                'ka': np.array([0.5, 0.5, 0.5]),
                'ks': np.array([0.8, 0.8, 0.8]),
                'shininess': 10.0
            },
            'view': {
                'axes': True,
                'cell_border': True,
                'perspective': False,
                'eye_position': np.array([0.0, 0.0, 20.0]),
                'center': np.array([0.0, 0.0, 0.0]),
                'up': np.array([0.0, 1.0, 0.0]),
                'projection': {
                    'fov': 90.0,
                    'near': 0.1,
                    'far': 100.0
                },
                'ortho': {
                    'left': -12.0,
                    'right': 12.0,
                    'top': 9.0,
                    'bottom': -9.0,
                }
            },
            'background': {
                'color': np.array([0.6, 0.6, 0.6, 1.0])
            },
            'fog': {
                'color': np.array([0.6, 0.6, 0.6, 1.0]),
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
        self.__control_params = {
            'only_keyboard_selection': True,
            'slider_speed': 1
        }
        self.__processing_params = {
            'delete_coordinates_after_leave_cell': True
        }
        self.__atom_colors = {
            'H': np.array([0.8, 0.8, 0.8]),
            'He': np.array([0.8, 0.8, 0.8]),
            'Li': np.array([0.8, 0.8, 0.8]),
            'Be': np.array([0.8, 0.8, 0.8]),
            'B': np.array([0.8, 0.8, 0.8]),
            'C': np.array([0.8, 0.8, 0.8]),
            'N': np.array([0.8, 0.8, 0.8]),
            'O': np.array([0.8, 0.8, 0.8]),
            'F': np.array([0.8, 0.8, 0.8]),
            'Ne': np.array([0.8, 0.8, 0.8]),
            'Na': np.array([0.8, 0.8, 0.8]),
            'Mg': np.array([0.8, 0.8, 0.8]),
            'Al': np.array([0.8, 0.8, 0.8]),
            'Si': np.array([0.8, 0.8, 0.8]),
            'P': np.array([0.8, 0.8, 0.8]),
            'S': np.array([0.8, 0.8, 0.8]),
            'Cl': np.array([0.8, 0.8, 0.8]),
            'Ar': np.array([0.8, 0.8, 0.8]),
            'K': np.array([0.8, 0.8, 0.8]),
            'Ca': np.array([0.8, 0.8, 0.8]),
            'Sc': np.array([0.8, 0.8, 0.8]),
            'Ti': np.array([0.8, 0.8, 0.8]),
            'V': np.array([0.8, 0.8, 0.8]),
            'Cr': np.array([0.8, 0.8, 0.8]),
            'Mn': np.array([0.8, 0.8, 0.8]),
            'Fe': np.array([0.8, 0.8, 0.8]),
            'Co': np.array([0.8, 0.8, 0.8]),
            'Ni': np.array([0.8, 0.8, 0.8]),
            'Cu': np.array([0.8, 0.8, 0.8]),
            'Zn': np.array([0.8, 0.8, 0.8]),
            'Ga': np.array([0.8, 0.8, 0.8]),
            'Ge': np.array([0.8, 0.8, 0.8]),
            'As': np.array([0.8, 0.8, 0.8]),
            'Se': np.array([0.8, 0.8, 0.8]),
            'Br': np.array([0.8, 0.8, 0.8]),
            'Kr': np.array([0.8, 0.8, 0.8]),
            'Rb': np.array([0.8, 0.8, 0.8]),
            'Sr': np.array([0.8, 0.8, 0.8]),
            'Y': np.array([0.8, 0.8, 0.8]),
            'Zr': np.array([0.8, 0.8, 0.8]),
            'Nb': np.array([0.8, 0.8, 0.8]),
            'Mo': np.array([0.8, 0.8, 0.8]),
            'Tc': np.array([0.8, 0.8, 0.8]),
            'Ru': np.array([0.8, 0.8, 0.8]),
            'Rh': np.array([0.8, 0.8, 0.8]),
            'Pd': np.array([0.8, 0.8, 0.8]),
            'Ag': np.array([0.8, 0.8, 0.8]),
            'Cd': np.array([0.8, 0.8, 0.8]),
            'In': np.array([0.8, 0.8, 0.8]),
            'Sn': np.array([0.8, 0.8, 0.8]),
            'Sb': np.array([0.8, 0.8, 0.8]),
            'Te': np.array([0.8, 0.8, 0.8]),
            'I': np.array([0.8, 0.8, 0.8]),
            'Xe': np.array([0.8, 0.8, 0.8]),
            'Cs': np.array([0.8, 0.8, 0.8]),
            'Ba': np.array([0.8, 0.8, 0.8]),
            'La': np.array([0.8, 0.8, 0.8]),
            'Ce': np.array([0.8, 0.8, 0.8]),
            'Pr': np.array([0.8, 0.8, 0.8]),
            'Nd': np.array([0.8, 0.8, 0.8]),
            'Pm': np.array([0.8, 0.8, 0.8]),
            'Sm': np.array([0.8, 0.8, 0.8]),
            'Eu': np.array([0.8, 0.8, 0.8]),
            'Gd': np.array([0.8, 0.8, 0.8]),
            'Tb': np.array([0.8, 0.8, 0.8]),
            'Dy': np.array([0.8, 0.8, 0.8]),
            'Ho': np.array([0.8, 0.8, 0.8]),
            'Er': np.array([0.8, 0.8, 0.8]),
            'Tm': np.array([0.8, 0.8, 0.8]),
            'Yb': np.array([0.8, 0.8, 0.8]),
            'Lu': np.array([0.8, 0.8, 0.8]),
            'Hf': np.array([0.8, 0.8, 0.8]),
            'Ta': np.array([0.8, 0.8, 0.8]),
            'W': np.array([0.8, 0.8, 0.8]),
            'Re': np.array([0.8, 0.8, 0.8]),
            'Os': np.array([0.8, 0.8, 0.8]),
            'Ir': np.array([0.8, 0.8, 0.8]),
            'Pt': np.array([0.8, 0.8, 0.8]),
            'Au': np.array([0.8, 0.8, 0.8]),
            'Hg': np.array([0.8, 0.8, 0.8]),
            'Tl': np.array([0.8, 0.8, 0.8]),
            'Pb': np.array([0.8, 0.8, 0.8]),
            'Bi': np.array([0.8, 0.8, 0.8]),
            'Po': np.array([0.8, 0.8, 0.8]),
            'At': np.array([0.8, 0.8, 0.8]),
            'Rn': np.array([0.8, 0.8, 0.8]),
            'Fr': np.array([0.8, 0.8, 0.8]),
            'Ra': np.array([0.8, 0.8, 0.8]),
            'Ac': np.array([0.8, 0.8, 0.8]),
            'Th': np.array([0.8, 0.8, 0.8]),
            'Pa': np.array([0.8, 0.8, 0.8]),
            'U': np.array([0.8, 0.8, 0.8]),
            'Np': np.array([0.8, 0.8, 0.8]),
            'Pu': np.array([0.8, 0.8, 0.8]),
            'Am': np.array([0.8, 0.8, 0.8]),
            'Cm': np.array([0.8, 0.8, 0.8]),
            'Bk': np.array([0.8, 0.8, 0.8]),
            'Cf': np.array([0.8, 0.8, 0.8]),
            'Es': np.array([0.8, 0.8, 0.8]),
            'Fm': np.array([0.8, 0.8, 0.8]),
            'Md': np.array([0.8, 0.8, 0.8]),
            'No': np.array([0.8, 0.8, 0.8]),
            'Lr': np.array([0.8, 0.8, 0.8]),
            'Rf': np.array([0.8, 0.8, 0.8]),
            'Db': np.array([0.8, 0.8, 0.8]),
            'Sg': np.array([0.8, 0.8, 0.8]),
            'Bh': np.array([0.8, 0.8, 0.8]),
            'Hs': np.array([0.8, 0.8, 0.8]),
            'Mt': np.array([0.8, 0.8, 0.8]),
            'Ds': np.array([0.8, 0.8, 0.8]),
            'Rg': np.array([0.8, 0.8, 0.8]),
            'Cn': np.array([0.8, 0.8, 0.8]),
            'Nh': np.array([0.8, 0.8, 0.8]),
            'Fl': np.array([0.8, 0.8, 0.8]),
            'Mc': np.array([0.8, 0.8, 0.8]),
            'Lv': np.array([0.8, 0.8, 0.8]),
            'Ts': np.array([0.8, 0.8, 0.8]),
            'Og': np.array([0.8, 0.8, 0.8])
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
                                  self.__control_params, self.__processing_params]
            for indx, json_data in enumerate(data):
                Settings.check_settings_keys(__settings_default[indx], json_data)
                self.convert_values_to(json_data, np.ndarray)
                match indx:
                    case 0:
                        self.__new_window_location = json_data
                    case 1:
                        self.__scene_params = json_data
                    case 2:
                        self.__control_params = json_data
                    case 3:
                        self.__processing_params = json_data
                #__settings_default[indx] = json_data
                #self.convert_values_to(__settings_default[indx], np.ndarray)
            logger.info(f"Settings loaded from {self.get_settings_filename()}")
            logger.debug(f"Window location: {self.__new_window_location}")
            logger.debug(f"Scene params: {self.__scene_params}")
            logger.debug(f"Control params: {self.__control_params}")
            logger.debug(f"Processing params: {self.__processing_params}")
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

    @staticmethod
    def convert_values_to(dict_object, obj_type):
        for key in dict_object:
            if isinstance(dict_object[key], dict):
                Settings.convert_values_to(dict_object[key], obj_type)
            elif obj_type == list and isinstance(dict_object[key], np.ndarray):
                dict_object[key] = dict_object[key].tolist()
            elif obj_type == np.ndarray and isinstance(dict_object[key], list):
                dict_object[key] = np.array(dict_object[key])

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
        return Settings.__get_dict_value(self.__control_params, *keys)

    def set_control_params(self, value, *keys):
        Settings.__set_dict_value(self.__control_params, value, *keys)

    def get_processing_params(self, *keys):
        return Settings.__get_dict_value(self.__processing_params, *keys)

    def set_processing_params(self, value, *keys):
        Settings.__set_dict_value(self.__processing_params, value, *keys)

    def save_settings(self):
        json_data = [self.__new_window_location, self.__scene_params, 
                     self.__control_params, self.__processing_params] 
        for data in json_data:
            self.convert_values_to(data, list)
        with open(self.get_settings_filename(), 'w') as file:
            json.dump(json_data, file, indent=4)
        logger.info(f"Json data saved to {self.get_settings_filename()}")
        logger.debug(f"Window location: {self.__new_window_location}")
        logger.debug(f"Scene params: {self.__scene_params}")
        logger.debug(f"Control params: {self.__control_params}")
        logger.debug(f"Processing params: {self.__processing_params}")
        return self
