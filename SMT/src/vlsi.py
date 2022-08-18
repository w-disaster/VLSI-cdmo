#!/usr/bin/python3
from vlsi_smt import vlsi_smt
from model.Circuit import Circuit
from model.Plate import Plate
from z3 import * 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import sys, getopt

def get_io_files(argv):
    short_opts = "i:o:"
    long_opts = ["input_file=", "output_file="]
    try:
        arguments, values = getopt.getopt(argv[1:], short_opts, long_opts)
        input_filename, output_filename = "", ""
        for (arg, v) in arguments:
            if arg in ("-i", "--input_file"):
                input_filename = v
            elif arg in ("-o", "--output_file"):
                output_filename = v

        if input_filename == "" or output_filename == "":
            print("Usage: specify input file [-i, --input_file] and output file [-o, --output_file]")
            sys.exit(0)
        return (input_filename, output_filename)
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

def plot_plate(plate):
    if plate:
        #fig, ax = plt.subplots(figsize=(10, 10))
        (w, h) = plate.get_dim()
         
        M = np.zeros((h, w))
        for i, circuit in enumerate(plate.get_circuits()):
            (x, y) = circuit.get_coordinate()
            (cw, ch) = circuit.get_dim()
            M[y : y + ch, x : x + cw] = i + 1

        M = np.flip(M)
        ax = plt.gca()
        ax.matshow(M, );


        ax.set_xticks(np.arange(-.5, w, 1))
        ax.set_yticks(np.arange(-.5, h, 1))
        ax.set_xticklabels(np.arange(0, w + 1, -1))
        ax.set_yticklabels(np.arange(h + 1, 0, -1))
        
        ax.grid(color='red', linestyle='-.', linewidth=1)
        
        plt.show()

def solve_vlsi(plate):
    start_time = time.time()

    # letsss go Z3
    plate = vlsi_smt(plate, rot=False)

    print("Elapsed time: {}, plate dim (w, h) = ({}, {})"
            .format(time.time() - start_time, plate.get_dim()[0], 
                plate.get_dim()[1]))

    plot_plate(plate)


if __name__ == "__main__":
    (input_filename, output_filename) = get_io_files(sys.argv)
    plate = read_input_file(input_filename)
    solve_vlsi(plate)
