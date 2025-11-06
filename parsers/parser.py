"""Abstract class for parsing calculation files."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import abc

__all__ = ["AbstractParser"]


class AbstractParser(abc.ABC):
    """Abstract class for parsing calculation files."""

    def __init__(self, folder_path):
        """Parser initialization function."""
        self.__folder_path = folder_path

    def read(self):
        """Reads calculation file."""
        pass

    def __call__(self):
        return self.read()
