#!/usr/bin/python3

class Plate:
    def __init__(self, dim, n, circuits):
        self._dim = dim
        self._n = n
        self._circuits = circuits

    def get_n(self):
        return self._n

    def get_circuits(self):
        return self._circuits

    def get_circuit(self, i):
        return self._circuit[i]

    def get_dim(self):
        return self._dim


class Circuit:
    def __init__(self, dim):
        self._dim = dim
        self._set_placed(False)

    def get_dim(self):
        return self._dim

    def get_coordinate(self):
        if self._is_placed():
            return self.get_coordinate
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
