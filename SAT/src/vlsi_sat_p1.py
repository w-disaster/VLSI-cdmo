from z3 import *
from itertools import combinations
from math import floor, ceil
from copy import copy
import numpy as np

def vlsi_sat(plate):
    # Z3 Optimize
    s = Solver()
   
    (n, (w, h_max), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())
    
    csw, csh = [], []
    for i in range(n):
        csw.append(cs[i].get_dim()[0])
        csh.append(cs[i].get_dim()[1])

    # Define upperbound and lowerbound                           
    max_x, max_y = max(csw), max(csh)
    h_min = max_y

    # -------------------------------------------------------------------
    # ORDER ENCODING

    # Z3 order encoding variables
    px = [[Bool(f"px{i}_{e}") for e in range(w)] for i in range(n)]
    py = [[Bool(f"py{i}_{f}") for f in range(h_max)] for i in range(n)]
  
    # Non-overlapping variables
    lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
    ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

    # Order encoding constraints
    for i in range(n):
        # px_i <= e ==> px_i <= e + 1
        for e in range(w - csw[i] - 1):
            s.add(Implies(px[i][e], px[i][e + 1]))
        # py_i <= f ==> py_i <= f + 1 
        for f in range(h_max - csh[i] - 1):
            s.add(Implies(py[i][f], py[i][f + 1]))

    # -------------------------------------------------------------------
    # NON-OVERLAPPING

    # Non-overlapping constraints
    s.add([Or(lr[i][j], lr[j][i], ud[i][j], ud[j][i]) 
        for (i, j) in combinations(range(n), 2)])
       
    for (i, j) in combinations(range(n), 2):
        # X-axis
        # (i, j)
        s.add([Or(Not(lr[i][j]), Not(px[j][k])) for k in range(csw[i])])
        s.add([Or(Not(lr[i][j]), px[i][k], Not(px[j][k + csw[i]])) 
            for k in range(w - csw[i])])
        # (j, i)
        s.add([Or(Not(lr[j][i]), Not(px[i][k])) for k in range(csw[j])])
        s.add([Or(Not(lr[j][i]), px[j][k], Not(px[i][k + csw[j]])) 
            for k in range(w - csw[j])])
        
        # Y-axis
        # (i, j)
        s.add([Or(Not(ud[i][j]), Not(py[j][k])) for k in range(csh[i])])
        s.add([Or(Not(ud[i][j]), py[i][k], Not(py[j][k + csh[i]])) 
            for k in range(h_max - csh[i])])
        # (j, i)
        s.add([Or(Not(ud[j][i]), Not(py[i][k])) for k in range(csh[j])])
        s.add([Or(Not(ud[j][i]), py[j][k], Not(py[i][k + csh[j]])) 
            for k in range(h_max - csh[j])])
        
    # Domain reduction  
    m = np.argmax([csh[k] * csw[k] for k in range(n)])    
    for i in range(n):
        # X-axis right border all True
        for e in range(w - csw[i], w):
            s.add(px[i][e])
        # Y-axis top border all True
        for f in range(h_max - csh[i], h_max):
            s.add(py[i][f])

        s.add([px[m][e] for e in range((w - csw[m]) // 2, w - csw[m])])
        s.add([py[m][f] for f in range((h_max - csh[m]) // 2, h_max - csh[m])])     
    
    s.add([Implies(csw[i] > floor((w - csw[j]) / 2), Not(lr[i][j])) 
        for (i, j) in combinations(range(n), 2)])
    s.add([Implies(csw[i] > floor((w - csw[m]) / 2), Not(lr[i][m]))
        for i in range(n)])

    s.add([Implies(csw[i] + csw[j] > w, And(Not(lr[i][j]), Not(lr[j][i])))
        for (i, j) in combinations(range(n), 2)])
    s.add([Implies(csh[i] + csh[j] > h_max, And(Not(ud[i][j]), Not(ud[j][i])))
        for (i, j) in combinations(range(n), 2)])

    s.add([Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
        And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))) for (i, j) in combinations(range(n), 2)])

    if s.check() == sat:
        m = s.model()
        # evaluate x and y
        x_ev = [[m.evaluate(px[i][e]) 
            for e in range(len(px[i]))] for i in range(len(px))]
        y_ev = [[m.evaluate(py[i][f]) 
            for f in range(len(py[i]))] for i in range(len(py))]

        for k in range(n):
            xc, yc = x_ev[k].index(True), y_ev[k].index(True)
            print(xc, yc)
            plate.get_circuit(k).set_coordinate((xc, yc))
            
        return True, plate
    return False, []
    

def vlsi(plate, rot):    
    
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())

    csw, csh = [], []

    for i in range(n):
        csw.append(cs[i].get_dim()[0])
        csh.append(cs[i].get_dim()[1])

    # Define upperbound and lowerbound                           
    max_x, max_y = max(csw), max(csh)

    max_block_per_w = floor(w / max_x)                                           
    h_max = ceil(sum(csh) / max_block_per_w) + 2
    h_min = ceil(sum([csw[i] * csh[i] for i in range(n)]) / w)
    #h_min = max_y

    # BISECTION METHOD 
    ub = h_max
    lb = h_min
    h = h_min
    f = False 
    while True:        
        plate.set_dim((w, h))
        pl = vlsi_sat(plate)
        # If SAT
        if pl[0]:
            last_plate = copy(pl[1])
            print("SAT, h: {}".format(h))
            ub = h
        else:
            print("UNSAT, h: {}".format(h))
            lb = h

        new_h = floor((ub + lb) / 2)
        if h == new_h:
            break
        h = floor((ub + lb) / 2) 
    return last_plate 
