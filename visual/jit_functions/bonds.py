"""Jit functions for bonds detection."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from numba import jit
from numba.core.types import int64
import numpy as np
import logging
logging.getLogger('numba').setLevel(logging.INFO)

__all__ = [
    "nonoptimal_dimension_search",
    "neighbours_search_body",
    "neighbours_search",
    "neighbours_search_between_types_body",
    "neighbours_search_between_types"
]


@jit(fastmath=True, nopython=True, cache=True)
def nonoptimal_dimension_search(positions, number_of_dividings):
    length = len(positions) - 1
    size_array = np.zeros((3, number_of_dividings + 1))
    delta_dim = np.zeros(3)
    for iteration in range(number_of_dividings + 1):
        step = iteration * length // number_of_dividings
        pos = positions[step].transpose()
        size_array[0] = pos[0].max() - pos[0].min()
        size_array[1] = pos[1].max() - pos[1].min()
        size_array[2] = pos[2].max() - pos[2].min()
    size_array = np.asarray(sizeArray)
    for index in range(3):
        delta_dim[index] = size_array[index].max() - size_array[index].min()
    return delta_dim.argsort()[-2]


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_body(num, index, positions, indexes, dimension, bond_length):
    highest_index = max_index = len(indexes) - num
    min_index = 0
    now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
    pos = positions[index][dimension]
    while True:
        index_comp = indexes[now_index - 1 + num]
        index_comp_next = indexes[now_index + num]
        statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
        statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
        if statement1 and not statement2:
            break
        elif now_index == highest_index - 1 and statement1 and statement2:
            now_index = highest_index
            break
        elif now_index == 0 and not statement1:
            break
        elif statement1 and statement2:
            min_index = now_index
            summary = now_index + max_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        else:
            max_index = now_index
            summary = now_index + min_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
    tracking_pos = positions[index]
    returning_indexes = []
    for another_index in indexes[num + 1:now_index + num]:
        target_pos = positions[another_index]
        length = np.linalg.norm(tracking_pos - target_pos)
        if length <= bond_length:
            returning_indexes.append(another_index)
    return np.array(returning_indexes)


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search(search_algorithm, positions, indexes, dimension, bond_length):
    neighbours = dict()
    indexes_cp = indexes[:-1]
    for num, index in enumerate(indexes_cp):
        neighbours[int(index)] = search_algorithm(num, index, positions, indexes, dimension, bond_length)
    return neighbours


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_between_types_body(index, positions, indexes, dimension, bond_length):
    highest_index = max_index = len(indexes)
    min_index = 0
    now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
    pos = positions[index][dimension]
    while True:
        index_comp = indexes[now_index - 1]
        index_comp_next = indexes[now_index]
        statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
        statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
        if statement1 and not statement2:
            break
        elif now_index == highest_index - 1 and statement1 and statement2:
            now_index = highest_index
            break
        elif now_index == 0 and not statement1:
            break
        elif statement1 and statement2:
            min_index = now_index
            summary = now_index + max_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        else:
            max_index = now_index
            summary = now_index + min_index
            now_index = summary // 2
    tracking_pos = positions[index]
    returning_indexes = []
    for another_index in indexes[:now_index]:
        target_pos = positions[another_index]
        length = np.linalg.norm(tracking_pos - target_pos)
        if length <= bond_length:
            returning_indexes.append(another_index)
    return np.array(returning_indexes)


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_between_types(search_algorithm, positions, indexes_type1, indexes_type2, dimension, bond_length):
    neighbours = dict()
    for _, index in enumerate(indexes_type1):
        neighbours[int64(index)] = search_algorithm(index, positions, indexes_type2, dimension, bond_length)
    return neighbours

