#!/usr/bin/python3
from vlsi_sat_p1_opt import vlsi_sat
from model.Circuit import Circuit
from model.Plate import Plate
from z3 import * 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import sys, getopt

def get_io_files(argv):
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
                rot = v == "True"

        if input_filename == "" or output_filename == "" or rot == "":
            print("""Usage: specify input file [-i, --input_file], output file
                    [-o, --output_file] and rotation [-r, --rotation]""")
            sys.exit(0)
        return (input_filename, output_filename, rot)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

def read_input_file(filename):
    with open(filename) as f:
        lines = [f[:-1] for f in f.readlines()]
        w, n = int(lines[0]), int(lines[1])
        cs_dim = [d.split() for d in lines[2:]]
        cs_dim = [(int(cw), int(ch)) for (cw, ch) in cs_dim]
        circuits = [Circuit(dim) for dim in cs_dim]
    return Plate((w,), n, circuits)

def write_output_file(filename, plate):
    with open(filename, "w") as f:
        f.write(str(plate.get_dim()[0]) + " " + str(plate.get_dim()[0]) + "\n")
        f.write(str(plate.get_n()) + "\n")
        for circuit in plate.get_circuits():
            f.write(str(circuit.get_dim()[0]) + " " + str(circuit.get_dim()[1]) + " ")
            f.write(str(circuit.get_coordinate()[0]) + " " +
                str(circuit.get_coordinate()[1]) + "\n")

def plot_plate(plate):
    if plate:
        fig, ax = plt.subplots(figsize=(10, 10))
        (w, h) = plate.get_dim()
         
        M = np.zeros((h, w))
        for i, circuit in enumerate(plate.get_circuits()):
            (x, y) = circuit.get_coordinate()
            (cw, ch) = circuit.get_dim()
            M[h - y - ch : h - y, x : x + cw] = i + 1
            ax.text(x, h - y - 1, i + 1, size=12, va='center', ha='center')

        ax.matshow(M, );

        ax.set_xticks(np.arange(-.5, w, 1))
        ax.set_yticks(np.arange(-.5, h, 1))

        ax.set_xticklabels(np.arange(0, w + 1, 1))
        ax.set_yticklabels(np.arange(h, -1, -1)) 
        
        ax.grid(color='black', linestyle='-', linewidth=1)        
        plt.show()

def solve_vlsi(plate, rot):
    start_time = time.time()

    set_param('parallel.enable', True)
    # letsss go Z3
    plate = vlsi_sat(plate)

    print("Elapsed time: {}, plate dim (w, h) = ({}, {})"
            .format(time.time() - start_time, plate.get_dim()[0], 
                plate.get_dim()[1]))

    return plate

if __name__ == "__main__":
    (input_filename, output_filename, rot) = get_io_files(sys.argv)
    plate = read_input_file(input_filename)
    plate = solve_vlsi(plate, rot)
    write_output_file(output_filename, plate)
    plot_plate(plate)
