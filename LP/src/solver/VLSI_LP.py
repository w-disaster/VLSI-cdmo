#!/usr/bin/python3
import pulp as pl
from pulp import *
from model.VLSISolver import *
from model.Plate import *
from math import floor, ceil
import numpy as np

class VLSI_LP(VLSISolver):
    def __init__(self, plate: Plate):
        self.plate = plate
        (self.n, (self.w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())

        self.csw, self.csh = [], []
        for i in range(self.n):
            self.csw.append(cs[i].get_dim()[0])
            self.csh.append(cs[i].get_dim()[1])
       
    def compute_lower_upper_bound(self, csw, csh, w, n):                                                            
        max_x, max_y = max(csw), max(csh)
        max_block_per_w = floor(w / max_x)      
        h_max = ceil(n * max_y / max_block_per_w)
        h_min = max_y 
        return (h_min, h_max)

    def solve_vlsi(self) -> Plate:
        (self.h_min, self.h_max) = self.compute_lower_upper_bound(self.csw, 
                self.csh, self.w, self.n)

        prob = LpProblem("VLSI", LpMinimize)

        solver_list = pl.listSolvers()
        path_to_cplex = r'/opt/ibm/ILOG/CPLEX_Studio_Community221/cplex/bin/x86-64_linux/cplex'
        solver = pl.CPLEX_CMD(path=path_to_cplex, timeLimit=180)

        x = [LpVariable("x{}".format(i + 1), 0, self.w - min(self.csw), LpInteger) for i in range(self.n)]
        y = [LpVariable("y{}".format(i + 1), 0, self.h_max - min(self.csh), LpInteger) for i in range(self.n)]
        
        delta = [[[LpVariable("delta{}-{}-{}".format(i + 1, j + 1, k + 1), 0, 1, cat="Integer") for j in range(self.n)]
                  for i in range(self.n)] for k in range(self.n)]
        
        h = LpVariable("Height", self.h_min, self.h_max, LpInteger)
        prob += h, "Height of the plate"

        for i in range(self.n):
            prob += x[i] + self.csw[i] <= self.w
            prob += y[i] + self.csh[i] <= h
            for j in range(self.n):
                if i < j:
                    prob += x[i] + self.csw[i] <= x[j] + self.w * (delta[i][j][0])
                    prob += x[j] + self.csw[j] <= x[i] + self.w * (delta[i][j][1])
                    prob += y[i] + self.csh[i] <= y[j] + self.h_max * (delta[i][j][2])
                    prob += y[j] + self.csh[j] <= y[i] + self.h_max * (delta[i][j][3])
                    prob += delta[i][j][0] + delta[i][j][1] + delta[i][j][2] + delta[i][j][3] <= 3
                    
        prob.solve(solver)
        
        self.plate.set_dim((self.w, int(h.varValue)))
        for i in range(self.n):
            self.plate.get_circuit(i).set_coordinate((int(x[i].varValue), int(y[i].varValue)))
        
        return self.plate
