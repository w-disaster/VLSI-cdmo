#!/usr/bin/python3
from model.Circuit import Circuit
from model.Plate import Plate
import sys, getopt
import re

"""
    Given the instance's filename as argument, this function creates n Circuit
    objects and adds them to a new Plate, which is returned.
"""
def instance_to_plate(filename):
    # Open the file
    with open(filename) as f:
        lines = [f[:-1] for f in f.readlines()]
        # Read the width of the plate and the number of circuits
        w, n = int(lines[0]), int(lines[1])
        # Split the space separated lines and read the circuits dimensions
        cs_dim = [d.split() for d in lines[2:]]
        cs_dim = [(int(cw), int(ch)) for (cw, ch) in cs_dim]
        # Array of Circuit(s)
        circuits = [Circuit(dim) for dim in cs_dim]
    return Plate((w,), n, circuits)

"""
    This function reads a Plate object and the filename of the output file and
    writes to it the solution computed by a solver.
    The output file contains the same informations of the instance but 
    the left bottom coordinates of each circuit is also specified.
"""
def plate_to_solution(filename, plate):
    with open(filename, "w") as f:
        f.write(str(plate.get_dim()[0]) + " " + str(plate.get_dim()[0]) + "\n")
        f.write(str(plate.get_n()) + "\n")
        for circuit in plate.get_circuits():
            f.write(str(circuit.get_dim()[0]) + " " + str(circuit.get_dim()[1]) + " ")
            f.write(str(circuit.get_coordinate()[0]) + " " +
                str(circuit.get_coordinate()[1]) + "\n")
