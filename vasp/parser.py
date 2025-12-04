"""Vasp parser class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import copy
import random
import traceback
import numpy as np
import logging
logger = logging.getLogger(__name__)

__all__ = ["Parser"]


def deleted_positions_to_none(direct_positions_array, positions_array):
    """
    Replaces deleted positions (marked by a value of 10.0) in the direct_positions_array with None.
    
    Args:
        direct_positions_array: The array containing direct positions to be processed.
        positions_array: The original positions array (not directly used in the function, but included in the parameter list).
    
    Returns:
        None
    """
    for arr_step in direct_positions_array:
        for atom in arr_step:
            for indx, proj in enumerate(atom):
                if proj == 10.:
                    atom[indx] = None


def atoms_info_filling(dictionary):
    """
    Args:
        dictionary: A dictionary containing atom information.
    
    Returns:
        dictionary: The input dictionary with added atom radii and color information.
    
    Method Details:
    This method fills in the color values and radii for each atom type
    present in the input dictionary. It initializes a dictionary
    `ATOMSINFO` within the input dictionary to store this information.
    The method iterates through the unique atom names and assigns default
    color values and radii based on the atom type. If an atom type is
    not recognized, it assigns a random color and radius. Finally, it
    populates a list `RADII` in the input dictionary with the radii
    corresponding to each atom in the `ATOMNAMES` list.
    
    Class Fields Initialized:
        ATOMSINFO: A dictionary to store color and radii information for each atom type.  Keys are atom names (strings), and values are dictionaries containing 'COLORVALUE' (NumPy array representing RGB color), 'RADII' (float representing atomic radius), and 'FILLED' (boolean indicating whether the information has been filled).
        RADII: A list of floats representing the radii of each atom, corresponding to the order of atoms in the 'ATOMNAMES' list.
    """
    #TODO: use settings for default atom colors and radii
    dictionary['RADII'] = []
    for _, name in enumerate(set(dictionary['ATOMNAMES'])):
        dictionary['ATOMSINFO'][name] = {'COLORVALUE': [], 'RADII': 1, 'FILLED': False}

    for i in range(dictionary['ATOMNUMBER']):
        atom = dictionary['ATOMNAMES'][i]
        now_filling_atom = dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]
        if not now_filling_atom['FILLED']:
            if atom == 'O':
                now_filling_atom['COLORVALUE'] = np.asarray([1, 0, 0]) # 'red'
                now_filling_atom['RADII'] = 0.3
            elif atom == 'Si':
                now_filling_atom['COLORVALUE'] = np.asarray([1, 1, 0])  # 'yellow'
                now_filling_atom['RADII'] = 0.4
            elif atom == 'H':
                now_filling_atom['COLORVALUE'] = np.asarray([0.5, 0.5, 0.5])  # 'gray'
                now_filling_atom['RADII'] = 0.2
            elif atom == 'C':
                now_filling_atom['COLORVALUE'] = np.asarray([0.2, 0.2, 0.2])  # 'black'
                now_filling_atom['RADII'] = 0.33
            elif atom == 'He':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 1, 0])  # 'green'
                now_filling_atom['RADII'] = 0.18
            elif atom == 'Ar':
                now_filling_atom['COLORVALUE'] = np.asarray([0.6, 0, 0.6])  # 'purple'
                now_filling_atom['RADII'] = 0.34
            elif atom == 'Xe':
                now_filling_atom['COLORVALUE'] = np.asarray([0.05, 0, 0.6])  # 'blue'
                now_filling_atom['RADII'] = 0.38
            elif atom == 'Mo':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 0.78, 0.78]) # old violet 0.63, 0, 0.63 '#00c6c6' #a100a1
                now_filling_atom['RADII'] = 0.5
            elif atom == 'S':
                now_filling_atom['COLORVALUE'] = np.asarray([1.0, 1.0, 0])  # '#ffff00'
                now_filling_atom['RADII'] = 0.36
            elif atom == 'N':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 0, 1]) # old light blue '#0000ff'
                now_filling_atom['RADII'] = 0.24
            elif atom == 'Ne':
                now_filling_atom['COLORVALUE'] = np.asarray([0.543, 0.27, 0.07])  # '#8b4513'
                now_filling_atom['RADII'] = 0.16
            elif atom == 'Cl':
                now_filling_atom['COLORVALUE'] = np.asarray([0.12, 0.77, 0.65])  # '1fc4a6'
                now_filling_atom['RADII'] = 0.3
            elif atom == 'F':
                now_filling_atom['COLORVALUE'] = np.asarray([0.5, 0.3, 0.0]) # '7f4d00'
                now_filling_atom['RADII'] = 0.32
            else:
                r, g, b = random.random(), random.random(), random.random()
                rad = random.uniform(0.24, 0.42)
                now_filling_atom['COLORVALUE'] = np.asarray([r, g, b])
                now_filling_atom['RADII'] = rad
            now_filling_atom['FILLED'] = True


    for i in range(dictionary['ATOMNUMBER']):
        dictionary['RADII'].append(dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]['RADII'])
    return dictionary


def form_atoms_with_nums_dict(parser_parameters):
    """
    Creates a dictionary mapping atom names to their indices in a list of atom names.
    
    Args:
        parser_parameters: A dictionary containing atom names and other parsing parameters.
    
    Initializes the following class fields:
        parser_parameters['ATOM-NUMBERS']: A dictionary where keys are atom names (stripped of trailing whitespace) and values are NumPy arrays of their corresponding indices in the original list of atom names.
    
    Returns:
        None. The method modifies the input dictionary `parser_parameters` in place.
    """
    parser_parameters['ATOM-NUMBERS'] = dict()
    for uniq_atom in set(parser_parameters['ATOMNAMES']):
        for number, atom in enumerate(parser_parameters['ATOMNAMES']):
            if atom == uniq_atom:
                stripped_atom = uniq_atom.rstrip()
                if stripped_atom in parser_parameters['ATOM-NUMBERS']:
                    parser_parameters['ATOM-NUMBERS'][stripped_atom].append(number)
                else:
                    parser_parameters['ATOM-NUMBERS'][stripped_atom] = [number]
    for key in parser_parameters['ATOM-NUMBERS']:
        parser_parameters['ATOM-NUMBERS'][key] = np.array(parser_parameters['ATOM-NUMBERS'][key])


class Parser:
    """
    Parses VASP XML files to extract and process atomic position data.
    
     This class provides methods for initializing the parser with a directory
     containing XML files, extracting parser parameters, identifying removed
     atoms between consecutive files, and constructing a position array.
    """
    def __init__(self, directory, parser_parameters_dict):
        """
        Initializes the parser with a directory and parser parameters.
        
        Args:
           directory (str): The directory containing the VASP XML files.
           parser_parameters_dict (dict): A dictionary of initial parser parameters.
        
        Class Fields Initialized:
           _to_return (dict): A dictionary to store the final parser parameters. Initialized with parser_parameters_dict.
           _parser_parameters (dict): A dictionary to store parser parameters, initialized with directory and default values.
           xmllist (list): A list to store the names of the XML files found in the directory.
           
        Returns:
           None. The method updates the _to_return dictionary with the parsed parameters.
        """
        self._to_return = parser_parameters_dict
        self._parser_parameters = {'DIRECTORY': directory, 'ATOMSINFO': dict(), 'CALC_TYPE': 'VASP', 'BREAKER': False, 'MESSAGE': ''}
        self.xmllist = []
        vaspnum = 0
        try:
            for vaspfile in os.listdir(directory):
                if vaspfile.endswith('.xml'):
                    vaspnum += 1
                    self._parser_parameters[vaspfile] = {'ATOMNAMES': [], 'ATOMNUMBER': 0, 'POMASS': [], 'POSITIONS': [], 'POTIM': 0., 'TYPE': []}
                    self.xmllist.append(vaspfile)
        except AttributeError as err:
            self._parser_parameters['BREAKER'] = True
            self._parser_parameters['MESSAGE'] = 'Exception occurred when watching for vaspruns in directory.\n' + traceback.format_exc()
        except FileNotFoundError as err:
            self._parser_parameters['BREAKER'] = True
            self._parser_parameters['MESSAGE'] = 'Exception occurred when watching for vaspruns in directory.\n' + traceback.format_exc()
        self.xmllist.sort()
        self._parser_parameters['XMLLIST'] = self.xmllist
        if vaspnum == 0:
            self._parser_parameters['BREAKER'] = True
            self._parser_parameters['MESSAGE'] = 'There are no Vasprun files in the directory.'
        elif vaspnum != 0:
            for xml in self.xmllist:
                potim_read, basis_read = True, True
                first_read_check, first_coord_read = True, True
                with open(os.path.join(directory, xml), 'r') as vasp:
                    while True:
                        line = vasp.readline()
                        if not line:
                            break
                        if '<atoms>' in line:
                            self._parser_parameters[xml]['ATOMNUMBER'] = int(line.split()[1])
                        if '<field type="int">atomtype</field>' in line:
                            vasp.readline()
                            for index in range(self._parser_parameters[xml]['ATOMNUMBER']):
                                atomtype = vasp.readline()
                                self._parser_parameters[xml]['ATOMNAMES'].append((atomtype.split('>')[2]).split('<')[0])
                                self._parser_parameters[xml]['TYPE'].append(int(atomtype.split('<')[4].split('>')[1]))
                        if potim_read and 'name="POTIM">' in line:
                            self._parser_parameters[xml]['POTIM'] = float(line.split()[2].split('<')[0])
                            potim_read = False
                        if 'name="POMASS">' in line:
                            for mass in line.split()[2:-1]:
                                self._parser_parameters[xml]['POMASS'].append(float(mass))
                            self._parser_parameters[xml]['POMASS'].append(float((line.split()[-1]).split('<')[0]))
                        if '<varray name="positions" >' in line:  # <varray name="positions" >
                            try:
                                if first_read_check:
                                    first_read_check = False
                                else:
                                    array = [list(map(float, vasp.readline().split()[1:4])) for _ in range(self._parser_parameters[xml]['ATOMNUMBER'])]
                                    if first_coord_read:
                                        self._parser_parameters[xml]['POSITIONS'].append(array)
                                        first_coord_read = False
                                    if array != self._parser_parameters[xml]['POSITIONS'][-1]:
                                        self._parser_parameters[xml]['POSITIONS'].append(array)
                            except Exception as err:
                                self._parser_parameters['BREAKER'] = True
                                self._parser_parameters['MESSAGE'] = 'There are mistakes with reading positions.\n' + traceback.format_exc()
                        if basis_read and '<varray name="basis" >' in line:
                            basis_str = [vasp.readline() for _ in range(3)]
                            basis = [list(map(float, basis_line.split()[1:4])) for basis_line in basis_str]
                            self._parser_parameters[xml]['BASIS'] = basis
                            basis_read = False
                self._parser_parameters[xml]['VASPLEN'] = len(self._parser_parameters[xml]['POSITIONS'])
            self._parser_parameters['MASSES'] = [self._parser_parameters[self.xmllist[0]]['POMASS'][index - 1] for index in self._parser_parameters[self.xmllist[0]]['TYPE']]
            self._parser_parameters['STEPS_LIST'] = [self._parser_parameters[self.xmllist[0]]['VASPLEN']]
            for xml in self.xmllist[1:]:
                self._parser_parameters['STEPS_LIST'].append(self._parser_parameters['STEPS_LIST'][-1] + self._parser_parameters[xml]['VASPLEN'] - 1)
            self._parser_parameters['STEPS'] = sum([self._parser_parameters[xml]['VASPLEN'] for xml in self.xmllist]) - len(self.xmllist) + 1
            self._parser_parameters['ATOMNAMES'] = self._parser_parameters[self.xmllist[0]]['ATOMNAMES']
            form_atoms_with_nums_dict(self._parser_parameters)
            self.removed_atoms_find(self._parser_parameters)
            self.position_array_form(self._parser_parameters)
            self._parser_parameters['POTIM'] = [self._parser_parameters[xml_file]['POTIM'] for xml_file in self._parser_parameters['XMLLIST']]
            if not self.breaker:
                try:
                    self._parser_parameters['POSITIONS'] = np.array(self._parser_parameters['POSITIONS'])
                    self._parser_parameters['BASIS'] = self._parser_parameters[self._parser_parameters['XMLLIST'][0]]['BASIS']
                    self._parser_parameters['ATOMNUMBER'] = self._parser_parameters[self._parser_parameters['XMLLIST'][0]]['ATOMNUMBER']
                    for i in range(self._parser_parameters['ATOMNUMBER']):
                        if self._parser_parameters['ATOMNAMES'][i][-1] == ' ':
                            self._parser_parameters['ATOMNAMES'][i] = self._parser_parameters['ATOMNAMES'][i][:-1]
                    self._parser_parameters['BASIS'] = np.array(self._parser_parameters['BASIS'])
                    cube_vert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                                 [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                                 [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
                    # Создание вершин границы ячейки
                    self._parser_parameters['BASIS_VERT'] = np.dot(np.asarray(cube_vert), self._parser_parameters['BASIS'])
                    self._parser_parameters['DIRECT'] = np.copy(self._parser_parameters['POSITIONS'])
                    self._parser_parameters['POSITIONS'] = self._parser_parameters['POSITIONS'] - 0.5
                    # Преобразование координат из дискретных в декартовы в соответствии с базисом
                    for m in range(self._parser_parameters['STEPS']):
                        self._parser_parameters['POSITIONS'][m] = np.dot(self._parser_parameters['POSITIONS'][m], self._parser_parameters['BASIS'])
                    deleted_positions_to_none(self._parser_parameters['DIRECT'], self._parser_parameters['POSITIONS'])
                    self._parser_parameters = atoms_info_filling(self._parser_parameters)
                    self._parser_parameters['ID'] = [self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self._parser_parameters['ATOMNUMBER'])]
                    self._parser_parameters['ID-TO-NUM'] = {self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self._parser_parameters['ATOMNUMBER'])}
                except KeyError as err:
                    self._parser_parameters['BREAKER'] = True
                    self._parser_parameters['MESSAGE'] = 'There are mistakes with reading positions and/or basis.\n' + traceback.format_exc()
        self._to_return.update(self._parser_parameters)

    def __call__(self, *args, **kwargs):
        """
        Returns the parser parameters.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The parser parameters stored in the _parser_parameters field.
        """
        return self._parser_parameters

    def removed_atoms_find(self, dictionary):
        """
        Finds atoms removed between consecutive XML files in a dictionary.
        
        This method compares the positions of atoms in consecutive XML files
        (identified by keys in the input dictionary) to determine which atoms
        have been removed. It updates the dictionary with a 'REMOVED' key
        for each XML file, indicating which atoms are no longer present
        compared to the previous file. It also checks for inconsistencies
        in atom counts between files and sets a 'BREAKER' flag if found.
        
        Args:
          self:  The instance of the class.
          dictionary: A dictionary containing XML data, where keys are XML
            file identifiers and values are dictionaries with 'POSITIONS' and
            'ATOMNUMBER' keys.
        
        Returns:
          None
        
        Class Fields Initialized:
          - self.breaker: A boolean flag indicating whether a parsing error
            (inconsistent atom counts) has been detected. Initialized to False.
        """
        xml = dictionary.get('XMLLIST')
        self.breaker = False
        if len(xml) > 1:
            for file in range(len(xml) - 1):
                index_f2, differ = 0, []
                for f1_element in dictionary[xml[file]]['POSITIONS'][-1]:
                    if f1_element == dictionary[xml[file + 1]]['POSITIONS'][0][index_f2]:
                        index_f2 += 1 if index_f2 < len(dictionary[xml[file + 1]]['POSITIONS'][0]) - 1 else 0
                        differ.append(False)
                    else:
                        differ.append(True)
                dictionary[xml[file + 1]]['REMOVED'] = differ
                if file != 0:
                    for index in range(len(dictionary[xml[file]]['REMOVED'])):
                        if dictionary[xml[file]]['REMOVED'][index]:
                            dictionary[xml[file + 1]]['REMOVED'].insert(index, True)
                if sum(differ) != dictionary[xml[0]]['ATOMNUMBER'] - dictionary[xml[file + 1]]['ATOMNUMBER']:
                    self._parser_parameters['BREAKER'] = True
                    self._parser_parameters['MESSAGE'] = 'Vasprun files present different calculations.'

    @staticmethod
    def position_array_form(dictionary):
        """
        Creates a position array from a dictionary of XML data.
        
        This method processes a dictionary containing XML data to construct a 'POSITIONS' array.
        It initializes the 'POSITIONS' array with the 'POSITIONS' data from the first XML entry,
        then iterates through the remaining XML entries, adding their 'POSITIONS' data to the
        'POSITIONS' array, while inserting placeholder values at specified indices based on
        the 'REMOVED' flags.
        
        Args:
            dictionary: A dictionary containing XML data, including 'XMLLIST', 'POSITIONS',
                and 'REMOVED' keys within nested structures.
        
        Returns:
            None. The method modifies the input dictionary in place by adding or updating
            the 'POSITIONS' key.
        """
        xml = dictionary['XMLLIST']
        dictionary['POSITIONS'] = copy.deepcopy(dictionary[xml[0]]['POSITIONS'])
        for positions in range(1, len(xml)):
            for different_pos in range(len(dictionary[xml[positions]]['REMOVED'])):
                if dictionary[xml[positions]]['REMOVED'][different_pos]:
                    for array_value in range(len(dictionary[xml[positions]]['POSITIONS'])):
                        dictionary[xml[positions]]['POSITIONS'][array_value].insert(different_pos, [10., 10., 10.])
            dictionary['POSITIONS'] += dictionary[xml[positions]]['POSITIONS'][1:]
