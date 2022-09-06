from z3 import *
from itertools import combinations
from math import floor, ceil
from model.Plate import Plate
from model.VLSISolver import VLSISolver
from copy import copy
import numpy as np

class VLSI_SAT_rot(VLSISolver):
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
        z = [Bool(f"z_{i}") for i in range(n)] 

        # Order encoding constraints
        for i in range(n):
            # px_i <= e ==> px_i <= e + 1
            for e in range(w - 1):
                s.add(Implies(px[i][e], px[i][e + 1]))
            # py_i <= f ==> py_i <= f + 1 
            for f in range(h_max - 1):
                s.add(Implies(py[i][f], py[i][f + 1]))

        for h in range(h_min, h_max):
            s.add([Or(Not(ph[h - h_min]), 
                Or([py[k][i] for i in range(h - csh[k] + 1)])) for k in range(n)])
            
            hc = And([If(z[k], And([py[k][i] for i in range(h - csh[k], h_max)]),
                And([py[k][i] for i in range(h - csw[k], h_max)])) for k in range(n)])
            s.add(Implies(ph[h - h_min], hc))

            # Order encoding
            if h < h_max - 1: 
                s.add(Or(Not(ph[h - h_min]), ph[h - h_min + 1]))
        return (px, py, ph, z)
    
    def non_overlapping_constraints(self, px, py, z, s, csw, csh, w, n, h_min, h_max):
        lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
        ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

        s.add([Or(lr[i][j], lr[j][i], ud[i][j], ud[j][i]) 
            for (i, j) in combinations(range(n), 2)])

        for (i, j) in combinations(range(n), 2):
            cx_ij_w, cx_ij_h = [], []
            cx_ji_w, cx_ji_h = [], []
            
            cy_ij_w, cy_ij_h = [], []
            cy_ji_w, cy_ji_h = [], []

            cx_ij_no_w, cx_ij_no_h = [], []
            cx_ji_no_w, cx_ji_no_h = [], []
     
            cy_ij_no_w, cy_ij_no_h = [], []
            cy_ji_no_w, cy_ji_no_h = [], []

            for k in range(h_max):
                # (i, j)
                # c{x, y}_ij
                if k < csw[i]:
                    cx_ij_w.append(Implies(lr[i][j], Not(px[j][k])))
                    cy_ij_w.append(Implies(ud[i][j], Not(py[j][k])))

                if k < csh[i]:
                    cx_ij_h.append(Implies(lr[i][j], Not(px[j][k])))
                    cy_ij_h.append(Implies(ud[i][j], Not(py[j][k])))
                
                # c{x, y}_no_ij 
                if k < w - csw[i]:
                    cx_ij_no_w.append(Implies(And(lr[i][j], px[j][k + csw[i]]), px[i][k]))
                if k < w - csh[i]:
                    cx_ij_no_h.append(Implies(And(lr[i][j], px[j][k + csh[i]]), px[i][k]))
                
                if k < h_max - csh[i]:
                    cy_ij_no_h.append(Implies(And(ud[i][j], py[j][k + csh[i]]), py[i][k]))
                if k < h_max - csw[i]:
                    cy_ij_no_w.append(Implies(And(ud[i][j], py[j][k + csw[i]]), py[i][k]))
                                
                # (j, i)
                # c{x, y}_ji
                if k < csw[j]:
                    cx_ji_w.append(Implies(lr[j][i], Not(px[i][k])))
                    cy_ji_w.append(Implies(ud[j][i], Not(py[i][k])))

                if k < csh[j]:
                    cx_ji_h.append(Implies(lr[j][i], Not(px[i][k])))
                    cy_ji_h.append(Implies(ud[j][i], Not(py[i][k])))
        
                # c{x, y}_no_ji
                if k < w - csw[j]:
                    cx_ji_no_w.append(Implies(And(lr[j][i], px[i][k + csw[j]]), px[j][k]))
                if k < w - csh[j]:
                    cx_ji_no_h.append(Implies(And(lr[j][i], px[i][k + csh[j]]), px[j][k]))
                
                if k < h_max - csh[j]:
                    cy_ji_no_h.append(Implies(And(ud[j][i], py[i][k + csh[j]]), py[j][k]))
                if k < h_max - csw[j]:
                    cy_ji_no_w.append(Implies(And(ud[j][i], py[i][k + csw[j]]), py[j][k]))

            
            # (i, j)
            s.add(If(z[i], And(And(cx_ij_w), And(cx_ij_no_w)), And(And(cx_ij_h), And(cx_ij_no_h))))
            s.add(If(z[i], And(And(cy_ij_h), And(cy_ij_no_h)), And(And(cy_ij_w), And(cy_ij_no_w))))

            # (j, i)
            s.add(If(z[j], And(And(cx_ji_w), And(cx_ji_no_w)), And(And(cx_ji_h), And(cx_ji_no_h))))
            s.add(If(z[j], And(And(cy_ji_h), And(cy_ji_no_h)), And(And(cy_ji_w), And(cy_ji_no_w))))

        return (lr, ud)

    def domain_reduction(self, px, py, z, s, csw, csh, w, n):
        # Domain reduction     
        for i in range(n):
            # X-axis right border all True  
            s.add(If(z[i], And([px[i][e] for e in range(w - csw[i], w)]),
                And([px[i][e] for e in range(w - csh[i], w)])))
        
        m = np.argmax([csh[k] * csw[k] for k in range(n)]) 

        max_cx = (And([px[m][e] for e in range(csw[m])]),
                And([px[m][e] for e in range(csh[m])]))
        max_cy = (And([py[m][f] for f in range(csh[m])]),
                And([py[m][f] for f in range(csw[m])]))

        s.add(If(z[m], And(max_cx[0], max_cy[0]), And(max_cx[1], max_cy[1])))

    def add_symmetry_breaking_constrains(self, lr, ud, s, csw, csh, w, n, h_max):
        bs_x, bs_y = [], []
        bs_ec = []
        for (i, j) in combinations(range(n), 2):

            bs_x.append(Implies(And(csw[i] + csw[j] > w,
                                csh[i] + csw[j] > w,
                                csw[i] + csh[j] > w,
                                csh[i] + csh[j] > w), And(Not(lr[i][j]), Not(lr[j][i]))))

            bs_y.append(Implies(And(csw[i] + csw[j] > h_max,
                                csh[i] + csw[j] > h_max,
                                csw[i] + csh[j] > h_max,
                                csh[i] + csh[j] > h_max), And(Not(ud[i][j]), Not(ud[j][i]))))
    
            bs_ec.append(Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
                And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))))


        s.add(And(And(bs_x), And(bs_y)))
        s.add(bs_ec)

    def solve_vlsi(self) -> Plate:
        # Compute lower and upper bound
        (self.h_min, self.h_max) = self.compute_lower_upper_bound(self.csw, self.csh, self.w, self.n)  
        
        # Order encoding
        (self.px, self.py, self.ph, self.z) = self.order_encode_variables(self.s, self.csw,
                self.csh, self.w, self.n, self.h_min, self.h_max)
        
        # Add no overlapping constraints
        (self.lr, self.ud) = self.non_overlapping_constraints(self.px, self.py, self.z,
                self.s, self.csw, self.csh, self.w, self.n, self.h_min, self.h_max)
       
        # Add symmetry breaking constraints if enabledù
        if self.sym_br_enabled: 
            self.add_symmetry_breaking_constrains(self.lr, self.ud, self.s, self.csw,
                    self.csh, self.w, self.n, self.h_max)
        
        # Add domain reduction if enabled
        if self.dom_red_enabled: 
            self.domain_reduction(self.px, self.py, self.z, self.s, self.csw,
                self.csh, self.w, self.n)

        # Bisection method to compute the optimal height
        ub, lb = self.h_max, self.h_min
        h = self.h_min
        while ub - lb > 1:
            ss = copy(self.s)
            ss.add(self.ph[h - self.h_min])
            if ss.check() == sat:
                m = ss.model()
                # evaluate x and y
                x_ev = [[m.evaluate(self.px[i][e], model_completion=True) 
                    for e in range(len(self.px[i]))] for i in range(self.n)]
                y_ev = [[m.evaluate(self.py[i][f], model_completion=True) 
                    for f in range(len(self.py[i]))] for i in range(self.n)]
                z_ev = [m.evaluate(self.z[i], model_completion=True) for i in range(self.n)]
                
                self.plate.set_dim((self.w, h))
                for k in range(self.n):
                    xc, yc = x_ev[k].index(True), y_ev[k].index(True)
                    self.plate.get_circuit(k).set_coordinate((xc, yc))                
                    if not z_ev[k]:
                        dim = self.plate.get_circuit(k).get_dim()
                        self.plate.get_circuit(k).set_dim((dim[1], dim[0]))

                last_plate = copy(self.plate)
                ub = h
            else:
                lb = h

            h = floor((ub + lb) / 2)
        return last_plate
