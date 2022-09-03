#!/usr/bin/python3
from abc import ABCMeta, abstractmethod
from model.Plate import Plate

class Strategy():
    @abstractmethod
    def solve_vlsi(plate: Plate):
        pass
