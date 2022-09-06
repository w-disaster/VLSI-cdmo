#!/usr/bin/python3
from utils.read_instance_write_sol import *
from utils.plot_plate import *
from solver.VLSI_SAT import *
from solver.VLSI_SAT_rot import *
from time import time
import sys, getopt

"""
    This function reads the arguments given to the script.
    To work correctly the user must specify the input and output filename
    and if the rotation is enabled or not (True/False).
"""
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

"""
    The solve function calls the SAT solver (with or without rotation)
    and computes the execution time.
    It returns the optimal plate computed by the solver
"""

def solve(plate, rot):
    if rot:
        solver = VLSI_SAT_rot(plate)
    else:
        solver = VLSI_SAT(plate)

    start_time = time()
    plate = solver.solve_vlsi()
    print("Elapsed time: {}, plate dim (w, h) = ({}, {})"
            .format(time() - start_time, plate.get_dim()[0], 
                plate.get_dim()[1]))

    return plate

if __name__ == "__main__":
    # Read arguments
    (input_filename, output_filename, rot) = get_argv(sys.argv)    
    # Plate from instance file
    plate = instance_to_plate(input_filename)
    # Solve the instance
    plate = solve(plate, rot)
    # Write the solution to file
    plate_to_solution(output_filename, plate)
    # Plot the plate
    plot_plate(plate)
