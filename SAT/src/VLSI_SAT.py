from z3 import *
from itertools import combinations
from math import floor, ceil
from Plate import Plate
from Strategy import Strategy
from copy import copy
import numpy as np

class VLSI_SAT(Strategy):
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

        # Z3 variables
        s = Solver()
        s.set('timeout', 300 * 1000)

        px = [[Bool(f"px{i}_{e}") for e in range(w)] for i in range(n)]
        py = [[Bool(f"py{i}_{f}") for f in range(h_max)] for i in range(n)]
        ph = [Bool(f"ph_{h}") for h in range(h_min, h_max)]

        # Non-overlapping variables
        lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
        ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

        csw, csh = [], []
        for i in range(n):
            csw.append(cs[i].get_dim()[0])
            csh.append(cs[i].get_dim()[1])

        # Order encoding constraints
        for i in range(n):
            # px_i <= e ==> px_i <= e + 1
            for e in range(w - 1):
                s.add(Implies(px[i][e], px[i][e + 1]))
            # py_i <= f ==> py_i <= f + 1 
            for f in range(h_max - 1):
                s.add(Implies(py[i][f], py[i][f + 1]))

        # -------------------------------------------------------------------
        # NON-OVERLAPPING

        # Non-overlapping constraints
        s.add([Or(lr[i][j], lr[j][i], ud[i][j], ud[j][i]) 
            for (i, j) in combinations(range(n), 2)])
           
        for (i, j) in combinations(range(n), 2):
            # X-axis
            # (i, j)
            s.add([Implies(lr[i][j], Not(px[j][k])) for k in range(csw[i])])
            
            s.add([Implies(And(lr[i][j], px[j][k + csw[i]]), px[i][k]) 
                for k in range(w - csw[i])])
            # (j, i)
            s.add([Implies(lr[j][i], Not(px[i][k])) for k in range(csw[j])])
            s.add([Implies(And(lr[j][i], px[i][k + csw[j]]), px[j][k]) 
                for k in range(w - csw[j])])
            
            # Y-axis
            # (i, j)
            s.add([Implies(ud[i][j], Not(py[j][k])) for k in range(csh[i])])
            s.add([Implies(And(ud[i][j], py[j][k + csh[i]]), py[i][k]) 
                for k in range(h_max - csh[i])])
            # (j, i)
            s.add([Implies(ud[j][i], Not(py[i][k])) for k in range(csh[j])])
            s.add([Implies(And(ud[j][i], py[i][k + csh[j]]), py[j][k]) 
                for k in range(h_max - csh[j])])
            
        # Domain reduction  
        m = np.argmax(csw)
        for i in range(n):
            # X-axis right border all True
            for e in range(w - csw[i], w):
                s.add(px[i][e])

        s.add([px[m][e] for e in range((w - csw[m]) // 2, w - csw[m])])
        s.add([py[m][f] for f in range((h_max - csh[m]) // 2, h_max - csh[m])])     
        #s.add([px[m][e] for e in range(w)])
        #s.add([py[m][f] for f in range(h_max)])
        s.add([Implies(csw[i] > floor((w - csw[j]) / 2), Not(lr[i][j])) 
            for (i, j) in combinations(range(n), 2)])
        s.add([Implies(csh[i] > floor((h_max - csh[j]) / 2), Not(ud[i][j])) 
            for (i, j) in combinations(range(n), 2)])


        s.add([Implies(csw[i] + csw[j] > w, And(Not(lr[i][j]), Not(lr[j][i])))
            for (i, j) in combinations(range(n), 2)])
        s.add([Implies(csh[i] + csh[j] > h_max, And(Not(ud[i][j]), Not(ud[j][i])))
            for (i, j) in combinations(range(n), 2)])

        s.add([Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
            And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))) for (i, j) in combinations(range(n), 2)])
        
        # Constraints    
        for h in range(h_min, h_max):
            s.add([Or(Not(ph[h - h_min]), 
                Or([py[k][i] for i in range(h - csh[k] + 1)])) for k in range(n)])
            
            s.add([Or(Not(ph[h - h_min]), And([py[k][i] 
                for i in range(h - csh[k], h_max)])) for k in range(n)])

            # Order encoding
            if h < h_max - 1: 
                s.add(Or(Not(ph[h - h_min]), ph[h - h_min + 1]))
        
        # Bisection method 
        ub, lb = h_max, h_min
        h = h_min
        while ub - lb > 1:
            ss = copy(s)
            ss.add(ph[h - h_min])
            if ss.check() == sat:
                print("SAT, h: {}".format(h))
                m = ss.model()
                # evaluate x and y
                x_ev = [[m.evaluate(px[i][e]) 
                    for e in range(len(px[i]))] for i in range(len(px))]
                y_ev = [[m.evaluate(py[i][f]) 
                    for f in range(len(py[i]))] for i in range(len(py))]
                
                plate.set_dim((w, h))
                for k in range(n):
                    xc, yc = x_ev[k].index(True), y_ev[k].index(True)
                    plate.get_circuit(k).set_coordinate((xc, yc))                
                
                last_plate = copy(plate)
                ub = h
            else:
                print("UNSAT, h: {}".format(h))
                lb = h
            h = floor((ub + lb) / 2)
        return last_plate
