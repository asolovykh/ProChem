"""Classes for parsing VASP calculation files."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import copy
import random
import traceback
import numpy as np
import logging
from typing import Optional
from enum import Enum
from parsers.parser import *

logger = logging.getLogger(__name__)


class VASPfileType(Enum):
    """Enum for VASP file types."""
    XML = 0
    OUTCAR = 1
    POSCAR = 2
    CONTCAR = 3
    CHGCAR = 4
    CHG = 5
    OSZICAR = 6
    DOSCAR = 7


class Parser(AbstractParser):
    """Class for parsing VASP calculation files."""

    def __init__(
        self,
        file_path: Optional[str] = None,
        calculation: Optional[Calculation] = None,
    ):
        """Parser initialization function."""
        super().__init__("VASP", file_path, calculation)
        self.__file_path = super().get_file_path()
        self.__calculation = super().get_calculation()
        self.define_file_type()

    def define_file_type(self):
        """Defines file type."""
        if self.__file_path.endswith(".xml"):
            self.__file_type = VASPfileType.XML
        elif self.__file_path.startswith("OUTCAR"):
            self.__file_type = VASPfileType.OUTCAR
        elif self.__file_path.startswith("POSCAR"):
            self.__file_type = VASPfileType.POSCAR
        elif self.__file_path.startswith("CONTCAR"):
            self.__file_type = VASPfileType.CONTCAR
        elif self.__file_path.startswith("CHGCAR"):
            self.__file_type = VASPfileType.CHGCAR
        elif self.__file_path.startswith("CHG"):
            self.__file_type = VASPfileType.CHG
        elif self.__file_path.startswith("OSZICAR"):
            self.__file_type = VASPfileType.OSZICAR
        elif self.__file_path.startswith("DOSCAR"):
            self.__file_type = VASPfileType.DOSCAR

    def read_vasprun(self):
        """Reads vasprun.xml files."""
        atoms_number, pomass, positions, forces = 0, [], [], []
        read_potim, basis_read, skip_pos_read = True, True, 0
        with open(self.__file_path, "r") as xml:
            while True:
                line = xml.readline()
                if not line:
                    break
                if "<atoms>" in line:
                    atoms_number = int(line.split()[1])
                    self.__calculation.species = np.empty(atoms_number, dtype='<U2')
                    self.__calculation.masses = np.zeros(atoms_number, dtype=np.float32)
                if '<field type="int">atomtype</field>' in line:
                    xml.readline()
                    for index in range(atoms_number):
                        atomtype = xml.readline()
                        self.__calculation.species[index] = atomtype.split(">")[2].split("<")[0].rstrip()

                    atom_idx, pomass_idx, atom_name = 0, 0, self.__calculation.species[0]
                    while atom_idx < atoms_number:
                        if self.__calculation.species[atom_idx] != atom_name:
                            atom_name = self.__calculation.species[atom_idx]
                            pomass_idx += 1
                        self.__calculation.masses[atom_idx] = pomass[pomass_idx]
                        atom_idx += 1
                if read_potim and 'name="POTIM">' in line:
                    self.__calculation.timestep = float(line.split()[2].split("<")[0])
                    read_potim = False
                if 'name="POMASS">' in line:
                    for mass in line.rstrip().rstrip('</v>').split()[2:]:
                        pomass.append(float(mass))
                if '<varray name="positions" >' in line:  # <varray name="positions" >
                    try:
                        if skip_pos_read < 2:
                            skip_pos_read += 1
                        else:
                            array = [
                                list(map(float, xml.readline().split()[1:4]))
                                for _ in range(atoms_number)
                            ]
                            positions.append(array)
                    except Exception as err:
                        logger.error(
                            f"There are mistakes with reading positions.\n{traceback.format_exc()}"
                        )
                if '<varray name="forces" >' in line:
                    try:
                        array = [
                            list(map(float, xml.readline().split()[1:4]))
                            for _ in range(atoms_number)
                        ]
                        forces.append(array)
                    except Exception as err:
                        logger.error(
                            f"There are mistakes with reading forces.\n{traceback.format_exc()}"
                        )
                if basis_read and '<varray name="basis" >' in line: # TODO: in some calculations cell can be changed. This case should be processed.
                    basis = [list(map(float, xml.readline().split()[1:4])) for _ in range(3)]
                    self.__calculation.cell = np.array(basis, dtype=np.float32)
                    basis_read = False
            self.__calculation.direct_positions = np.array(positions, dtype=np.float32) - 0.5
            self.__calculation.positions = self.__calculation.direct_positions @ self.__calculation.cell
            self.__calculation.forces = np.array(forces, dtype=np.float32)

    def read(self):
        """Reads calculation file."""
        match self.__file_type:
            case VASPfileType.XML:
                self.read_vasprun()
            case VASPfileType.OUTCAR:
                pass
            case VASPfileType.POSCAR:
                pass
            case VASPfileType.CONTCAR:
                pass
            case VASPfileType.CHGCAR:
                pass
            case VASPfileType.CHG:
                pass
            case VASPfileType.OSZICAR:
                pass
            case VASPfileType.DOSCAR:
                pass
