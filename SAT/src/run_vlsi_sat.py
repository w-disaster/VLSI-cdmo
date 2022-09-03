#!/usr/bin/python3
from model.Circuit import Circuit
from model.Plate import Plate
from utils.read_instance_write_sol import *
from utils.plot_plate import *
from z3 import * 

from solver.VLSI_SAT import *
from solver.VLSI_SAT_rot import *
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from time import time
import sys, getopt

def get_argv(argv):
    short_opts = "i:o:r:"
    long_opts = ["input_file=", "output_file=", "rotation="]
    try:
        arguments, values = getopt.getopt(argv[1:], short_opts, long_opts)
        input_filename, output_filename, rot = "", "", ""
        for (arg, v) in arguments:
            if arg in ("-i", "--input_file"):
                input_filename = v
            elif arg in ("-o", "--output_file"):
                output_filename = v
            elif arg in ("-r", "--rotation"):
                rot = (v == "True")

        if input_filename == "" or output_filename == "" or rot == "":
            print("""Usage: specify input file [-i, --input_file], output file
                    [-o, --output_file] and rotation [-r, --rotation]""")
            sys.exit(0)
        return (input_filename, output_filename, rot)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

def solve(plate, rot):
    if rot:
        solver = VLSI_SAT_rot()
    else:
        solver = VLSI_SAT()

    start_time = time()
    plate = solver.solve_vlsi(plate)
    print("Elapsed time: {}, plate dim (w, h) = ({}, {})"
            .format(time() - start_time, plate.get_dim()[0], 
                plate.get_dim()[1]))

    return plate

def solve_all_instances(solver):
    n_instances = 40
    # All but the last instance
    for i in range(22, n_instances):
        plate = instance_to_plate("../../../instances/ins-" + str(i) + ".txt")
        start_time = time()

        # Solve VLSI
        plate = solver.solve_vlsi(plate)

        print("Instance n. {}".format(i))
        print("Elapsed time: {}, plate dim (w, h) = ({}, {})"
                    .format(time() - start_time, plate.get_dim()[0],
                        plate.get_dim()[1]))
        plot_plate(plate)

if __name__ == "__main__":
    (input_filename, output_filename, rot) = get_argv(sys.argv)
    
    plate = instance_to_plate(input_filename)
    
    plate = solve(plate, rot)
    plate_to_solution(output_filename, plate)
    plot_plate(plate)
