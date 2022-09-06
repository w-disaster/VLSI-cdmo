from z3 import *
from itertools import combinations
from math import floor, ceil
from model.Plate import Plate
from model.VLSISolver import VLSISolver
from copy import copy
import numpy as np

class VLSI_SAT(VLSISolver):
    def __init__(self, plate: Plate, sym_br_enabled=True, dom_red_enabled=True):
        self.plate = plate
        (self.n, (self.w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())
        self.sym_br_enabled = sym_br_enabled
        self.dom_red_enabled = dom_red_enabled

        self.csw, self.csh = [], []
        for i in range(self.n):
            self.csw.append(cs[i].get_dim()[0])
            self.csh.append(cs[i].get_dim()[1])

        self.s = Solver()
        self.s.set('timeout', 300 * 100)
        
    def compute_lower_upper_bound(self, csw, csh, w, n):                           
        max_x, max_y = max(csw), max(csh)

        max_block_per_w = floor(w / max_x)      
        A = sum([csw[i] * csh[i] for i in range(n)])
        h_max = ceil(n * max_y / max_block_per_w)
        h_min = max(ceil(A / w), max_y) 
        return (h_min, h_max)
       
    def order_encode_variables(self, s, csw, csh, w, n, h_min, h_max):
        px = [[Bool(f"px{i}_{e}") for e in range(w)] for i in range(n)]
        py = [[Bool(f"py{i}_{f}") for f in range(h_max)] for i in range(n)]
        ph = [Bool(f"ph_{h}") for h in range(h_min, h_max)]

        # Order encoding constraints
        for i in range(n):
            # px_i <= e ==> px_i <= e + 1
            for e in range(w - 1):
                s.add(Implies(px[i][e], px[i][e + 1]))
            # py_i <= f ==> py_i <= f + 1 
            for f in range(h_max - 1):
                s.add(Implies(py[i][f], py[i][f + 1]))

        # Constraints    
        for h in range(h_min, h_max):
            s.add([Or(Not(ph[h - h_min]), 
                Or([py[k][i] for i in range(h - csh[k] + 1)])) for k in range(n)])
            
            s.add([Or(Not(ph[h - h_min]), And([py[k][i] 
                for i in range(h - csh[k], h_max)])) for k in range(n)])

            # Order encoding
            if h < h_max - 1: 
                s.add(Or(Not(ph[h - h_min]), ph[h - h_min + 1]))
        return (px, py, ph)
    
    def non_overlapping_constraints(self, px, py, s, csw, csh, w, n, h_min, h_max):
        lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
        ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

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
        return (lr, ud)
     
    def domain_reduction(self, px, py, lr, ud, s, csw, csh, w, n, h_max):
        # Domain reduction  
        m = np.argmax([csw[k] * csh[k] for k in range(n)])
        for i in range(n):
            # X-axis right border all True
            for e in range(w - csw[i], w):
                s.add(px[i][e])
        
        s.add([px[m][e] for e in range(floor((w - csw[m]) / 2), w)])
        s.add([py[m][f] for f in range(floor((h_max - csh[m]) / 2), h_max)])
         
        s.add([Implies(csw[i] > floor((w - csw[m]) / 2), Not(lr[i][m])) 
            for i in range(n)])
        s.add([Implies(csh[i] > floor((h_max - csh[m]) / 2), Not(ud[i][m])) 
            for i in range(n)])
        

    def add_symmetry_breaking_constrains(self, lr, ud, s, csw, csh, w, n, h_max):
        s.add([Implies(csw[i] + csw[j] > w, And(Not(lr[i][j]), Not(lr[j][i])))
            for (i, j) in combinations(range(n), 2)])
        s.add([Implies(csh[i] + csh[j] > h_max, And(Not(ud[i][j]), Not(ud[j][i])))
            for (i, j) in combinations(range(n), 2)])

        s.add([Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
            And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))) for (i, j) in combinations(range(n), 2)])
        
    def solve_vlsi(self) -> Plate:
        # Compute lower and upper bound
        (self.h_min, self.h_max) = self.compute_lower_upper_bound(self.csw, self.csh, self.w, self.n)  
        
        # Order encoding
        (self.px, self.py, self.ph) = self.order_encode_variables(self.s, self.csw,
                self.csh, self.w, self.n, self.h_min, self.h_max)
        
        # Add no overlapping constraints
        (self.lr, self.ud) = self.non_overlapping_constraints(self.px, self.py, 
                self.s, self.csw, self.csh, self.w, self.n, self.h_min, self.h_max)
       
        # Add symmetry breaking constraints if enabled
        if self.sym_br_enabled: 
            self.add_symmetry_breaking_constrains(self.lr, self.ud, self.s, self.csw,
                    self.csh, self.w, self.n, self.h_max)
        
        # Add domain reduction if enabled
        if self.dom_red_enabled: 
            self.domain_reduction(self.px, self.py, self.lr, self.ud, self.s, self.csw,
                self.csh, self.w, self.n, self.h_max)

        # Bisection method to compute the optimal height
        ub, lb = self.h_max, self.h_min
        h = self.h_min
        while ub - lb > 1:
            ss = copy(self.s)
            ss.add(self.ph[h - self.h_min])
            if ss.check() == sat:
                m = ss.model()
                # evaluate x and y
                x_ev = [[m.evaluate(self.px[i][e]) 
                    for e in range(len(self.px[i]))] for i in range(len(self.px))]
                y_ev = [[m.evaluate(self.py[i][f]) 
                    for f in range(len(self.py[i]))] for i in range(len(self.py))]
                
                self.plate.set_dim((self.w, h))
                for k in range(self.n):
                    xc, yc = x_ev[k].index(True), y_ev[k].index(True)
                    self.plate.get_circuit(k).set_coordinate((xc, yc))                
                
                last_plate = copy(self.plate)
                ub = h
            else:
                lb = h
            h = floor((ub + lb) / 2)
        return last_plate
