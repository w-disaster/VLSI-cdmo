#!/usr/bin/python3
from abc import ABCMeta, abstractmethod
from model.Plate import Plate

"""
    The VLSISolver class describes what a solver must implement in order to be
    a VLSI one.
    This Strategy pattern is both used for the SAT and LP versions.
"""
class VLSISolver():
    @abstractmethod
    def solve_vlsi() -> Plate:
        pass
