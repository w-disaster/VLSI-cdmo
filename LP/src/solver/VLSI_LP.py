#!/usr/bin/python3
import pulp as pl
from pulp import *
from model.Strategy import *
from model.Plate import *
from math import floor, ceil
import numpy as np

class VLSI_LP(Strategy):
    def solve_vlsi(self, plate: Plate) -> Plate:
        (n, (w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())
        
        csw, csh = [], []
        for i in range(n):
            csw.append(cs[i].get_dim()[0])
            csh.append(cs[i].get_dim()[1])

        # Define upperbound and lowerbound                           
        max_x, max_y = max(csw), max(csh)

        max_block_per_w = floor(w / max_x)      
        A = sum([csw[i] * csh[i] for i in range(n)])
        h_max = ceil(n * max_y / max_block_per_w) + 2
        h_min = max(ceil(A / w), max_y) 

        # LP
        prob = LpProblem("VLSI", LpMinimize)

        solver_list = pl.listSolvers()
        path_to_cplex = r'C:\Program Files\IBM\ILOG\CPLEX_Studio_Community221\cplex\bin\x64_win64\cplex.exe'
        solver = pl.CPLEX_CMD(path=path_to_cplex, timeLimit=180)

        x = [LpVariable("x{}".format(i + 1), 0, w - min(csw), LpInteger) for i in range(n)]
        y = [LpVariable("y{}".format(i + 1), 0, h_max - min(csh), LpInteger) for i in range(n)]
        
        delta = [[[LpVariable("delta{}-{}-{}".format(i + 1, j + 1, k + 1), 0, 1, cat="Integer") for j in range(n)]
                  for i in range(n)] for k in range(n)]
        
        h = LpVariable("Height", h_min, h_max, LpInteger)
        prob += h, "Height of the plate"

        for i in range(n):
            prob += x[i] + csw[i] <= w
            prob += y[i] + csh[i] <= h
            for j in range(n):
                if i < j:
                    prob += x[i] + csw[i] <= x[j] + w * (delta[i][j][0])
                    prob += x[j] + csw[j] <= x[i] + w * (delta[i][j][1])
                    prob += y[i] + csh[i] <= y[j] + h_max * (delta[i][j][2])
                    prob += y[j] + csh[j] <= y[i] + h_max * (delta[i][j][3])
                    prob += delta[i][j][0] + delta[i][j][1] + delta[i][j][2] + delta[i][j][3] <= 3
                    
        prob.solve(solver)
        
        plate.set_dim((w, int(h.varValue)))
        for i in range(n):
            plate.get_circuit(i).set_coordinate((int(x[i].varValue), int(y[i].varValue)))
        
        return plate
