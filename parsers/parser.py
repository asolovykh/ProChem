"""Abstract class for parsing calculation files."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any

__all__ = ["AbstractParser", "Calculation"]


@dataclass
class CalculationError:
    exist: bool = False
    message: str = ""


@dataclass
class Calculation:
    """Calculation data class."""

    name: str
    directory: str
    calculation_type: str
    species: Optional[np.ndarray] = None
    masses: Optional[np.ndarray] = None
    cell: Optional[np.ndarray] = None
    timestep: Optional[float] = None
    positions: Optional[np.ndarray] = None
    direct_positions: Optional[np.ndarray] = None
    velocities: Optional[np.ndarray] = None
    forces: Optional[np.ndarray] = None
    streses: Optional[np.ndarray] = None
    energy: Optional[np.ndarray | float] = None
    charges: Optional[np.ndarray] = None
    errors: CalculationError = field(default_factory=CalculationError)
    extra: Optional[dict | Any] = None


class AbstractParser(ABC):
    """Abstract class for parsing calculation files."""

    def __init__(
        self,
        calculation_type: str,
        file_path: Optional[str] = None,
        calculation: Optional[Calculation] = None,
    ):
        """Parser initialization function."""
        match file_path, calculation:
            case None, None:
                raise ValueError("Folder path or calculation object must be specified.")
            case None, Calculation():
                self.__calculation = calculation
                self.__file_path = os.path.join(calculation.directory, calculation.name)
            case str(), None:
                self.__file_path = file_path
                self.__calculation = Calculation(
                    name=os.path.basename(self.__file_path),
                    directory=os.path.dirname(self.__file_path),
                    calculation_type=calculation_type,
                )
            case _:
                self.__file_path = file_path
                self.__calculation = calculation
                assert (
                    self.__calculation.calculation_type == calculation_type
                ), "Calculation type does not match."
                assert (
                    self.__calculation.directory == os.path.dirname(self.__file_path) and self.__calculation.name == os.path.basename(self.__file_path)
                ), "File path and file name does not match."

    def get_file_path(self):
        return self.__file_path

    def get_calculation(self):
        return self.__calculation

    @abstractmethod
    def read(self):
        """Reads calculation file."""
        pass

    def get_calculation(self):
        return self.__calculation

    def __repr__(self):
        return f"Parser obj at {hex(id(self))} with the following calculation:\n{self.__calculation}"
