#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

"""
    This function plots a Plate given as argument in the form
    of a grid, where at the bottom left cell of each circuit
    it's displayed its instance number. 
"""
def plot_plate(plate, instance_no=""):
    if plate:
        fig, ax = plt.subplots(figsize=(30, 10))
        (w, h) = plate.get_dim()
        
        # Read the Plate object building the matrix
        M = np.zeros((h, w))
        for i, circuit in enumerate(plate.get_circuits()):
            (x, y) = circuit.get_coordinate()
            (cw, ch) = circuit.get_dim()
            M[h - y - ch : h - y, x : x + cw] = i + 1
            ax.text(x, h - y - 1, i + 1, size=11, va='center', ha='center')

        if instance_no != "":
            ax.set_title("Instance no. {}".format(instance_no))
        # Show the matrix
        ax.matshow(M, );

        ax.xaxis.set_ticks_position('bottom')
        ax.set_xticks(np.arange(-.5, w, 1))
        ax.set_yticks(np.arange(-.5, h, 1))

        ax.set_xticklabels(np.arange(0, w + 1, 1))
        ax.set_yticklabels(np.arange(h, -1, -1)) 

        ax.grid(color="black", linestyle="dashed", linewidth=0.5)
        # Plot
        plt.show()
