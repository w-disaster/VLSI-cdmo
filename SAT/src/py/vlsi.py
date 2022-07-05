#!/usr/bin/python3

from vlsi_sat import vlsi_sat
from z3 import * 
import numpy as np
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
        b = [d.split() for d in lines[2:]]
        b = [(int(bw), int(bh)) for (bw, bh) in b]
    return (n, b, w)

def solve_vlsi(n, b, w):
    start_time = time.time()
    # Run SAT solver
    h, lfc = vlsi_sat(n, b, w, rot=True)

    print("h: {}, lfc: {}, elapsed time: {}".format(h, lfc, 
        time.time() - start_time))

    if len(lfc) > 0:
        #Plot
        fig, ax = plt.subplots(figsize=(10, 10))

        M = np.zeros((h - 1, w - 1))
        for i, (x, y) in enumerate(lfc):
            print(i, x, y)
            M[y : y + b[i][1], x : x + b[i][0]] = i + 1

        M = np.flip(M)
        ax.matshow(M, );
        plt.show()

if __name__ =="__main__":
    (input_filename, outout_filename) = get_io_files(sys.argv)
    (n, b, w) = read_input_file(input_filename)
    solve_vlsi(n, b, w)
