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
        return self._circuits[i]

    def get_dim(self):
        return self._dim

    def set_dim(self, dim):
        self._dim = dim
