#!/usr/bin/python3
"""
    In the VLSI problem, a Circuit is defined as a rectangle of dimension
    (width, height), eventually with its left bottom corner placed in
    a cell of coordinates (x, y) inside a plate.
"""
class Circuit:
    def __init__(self, dim):
        self._dim = dim
        self._set_placed(False)

    def get_dim(self):
        return self._dim

    def get_coordinate(self):
        if self._is_placed():
            return self._coordinate
        return (-1, -1)

    def set_dim(self, dim):
        self._dim = dim

    def set_coordinate(self, coordinate):
        if not self._is_placed():
            self._coordinate = coordinate
            self._set_placed(True)

    def _set_placed(self, placed):
        self._placed = placed

    def _is_placed(self):
        return self._placed
