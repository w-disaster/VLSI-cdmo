from z3 import *
from itertools import combinations
from math import floor, ceil
from copy import copy

def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one_np(bool_vars):
    return And(at_least_one_np(bool_vars), And(at_most_one_np(bool_vars)))

def z3_max(v):
    v_max = v[0]
    for i in range(1, len(v)):
        v_max = If(v_max > v[i], v_max, v[i])
    return v_max

def vlsi_sat(plate):
    (n, (w, h_max), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())

    csw, csh = [], []
    for i in range(n):
        csw.append(cs[i].get_dim()[0])
        csh.append(cs[i].get_dim()[1])

    """
    # Define upperbound and lowerbound                           
    max_x, max_y = max(csw), max(csh)

    max_block_per_w = floor(w / max_x)                                           
    h_max = ceil(sum(csh) / max_block_per_w) + 2
    h_min = max_y
    """

    # Z3 Optimize
    s = Solver()
    
    # -------------------------------------------------------------------
    # ORDER ENCODING

    # Z3 order encoding variables
    x = [[Bool(f"x{i}_{e}") for e in range(w - csw[i] + 1)]
        for i in range(n)]
    
    y = [[Bool(f"y{i}_{f}") for f in range(h_max - csh[i] + 1)]
        for i in range(n)]
   
    s.add([exactly_one_np(x[i]) for i in range(n)])
    s.add([exactly_one_np(y[i]) for i in range(n)])

    # -------------------------------------------------------------------
    # NON-OVERLAPPING

    # Non-overlapping variables
    lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
    ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

    # Non-overlapping constraints
    s.add([Or(Xor(lr[i][j], lr[j][i]), Xor(ud[i][j], ud[j][i])) 
        for (i, j) in combinations(range(n), 2)])
    
    for (i, j) in combinations(range(n), 2):   
        lr_ij, lr_ji, ud_ij, ud_ji = [], [], [], []

        # X-axis
        for t in range(w - csw[i] - csw[j] + 1):
            lr_ij_c, lr_ji_c = [], [] 
            for k in range(t, w - csw[i] - csw[j] + 1):
                lr_ij_c.append(x[j][k + csw[i]])
                lr_ji_c.append(x[i][k + csw[j]])

            lr_ij.append(And(x[i][t], Or(lr_ij_c)))
            lr_ji.append(And(x[j][t], Or(lr_ji_c)))       
        s.add(lr[i][j] == Or(lr_ij))
        s.add(lr[j][i] == Or(lr_ji))

        # Y-axis
        for t in range(h_max - csh[i] - csh[j] + 1):
            ud_ij_c, ud_ji_c = [], []
            for k in range(t, h_max - csh[i] - csh[j] + 1):
                ud_ij_c.append(y[j][k + csh[i]])
                ud_ji_c.append(y[i][k + csh[j]])
            
            ud_ij.append(And(y[i][t], Or(ud_ij_c)))
            ud_ji.append(And(y[j][t], Or(ud_ji_c)))
        s.add(ud[i][j] == Or(ud_ij))
        s.add(ud[j][i] == Or(ud_ji))
    
    s.add([Implies(csw[i] > floor((w - csw[j]) / 2), Not(lr[i][j])) 
        for (i, j) in combinations(range(n), 2)])

    s.add([Implies(csw[i] + csw[j] > w, And(Not(lr[i][j]), Not(lr[j][i])))
        for (i, j) in combinations(range(n), 2)])

    s.add([Implies(csh[i] + csh[j] > h_max, And(Not(ud[i][j]), Not(ud[j][i])))
        for (i, j) in combinations(range(n), 2)])

    s.add([Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
        And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))) for (i, j) in combinations(range(n), 2)])
    
    # --------------------------------------------------------------------
    # CHECK SAT

    if s.check() == sat:
        m = s.model()
        # x
        x_ev = [[m.evaluate(x[i][e], model_completion=True) for e in range(len(x[i]))] for i in range(len(x))]
        # y
        y_ev = [[m.evaluate(y[i][f], model_completion=True) for f in range(len(y[i]))] for i in range(len(y))]

        for k in range(n):
            xc, yc = x_ev[k].index(True), y_ev[k].index(True)
            print(xc, yc)
            plate.get_circuit(k).set_coordinate((xc, yc))    
        return True, plate
    return False, []


def vlsi(plate, rot):    
    
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

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
