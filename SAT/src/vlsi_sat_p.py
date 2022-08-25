from z3 import *
from itertools import combinations
from math import floor, ceil
import copy

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

def vlsi_sat(plate, rot):
    exactly_one = exactly_one_np
    
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

    csw, csh = [], []
    for i in range(n):
        csw.append(cs[i].get_dim()[0])
        csh.append(cs[i].get_dim()[1])

    # Define upperbound and lowerbound                           
    max_x, max_y = max(csw), max(csh)

    max_block_per_w = floor(w / max_x)                                           
    h_max = ceil(sum(csh) / max_block_per_w) 
    h_min = max_y

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

    # Order encoding constraints
    # px_i <= c --> px_i <= c + 1
    #for i in range(n):
    #    s.add([Or(Not(px[i][c]), px[i][c + 1]) 
    #        for c in range(w - csw[i])])
    #    s.add([Or(Not(py[i][c]), py[i][c + 1]) 
    #        for c in range(h_max - csh[i])])

    # -------------------------------------------------------------------
    # NON-OVERLAPPING

    # Non-overlapping variables
    lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
    ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

    # Non-overlapping constraints
    s.add([Or(lr[i][j], lr[j][i], ud[i][j], ud[j][i]) 
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
    
    # -------------------------------------------------------------------
    # ENCODING HEIGHT
    ph = [Bool(f"ph_{h}") for h in range(h_min, h_max)]

    # Constraints
    for h in range(h_min, h_max):
        # ph_h --> py_{k, h - ch_k}
        #s.add([Or(Not(ph[h - h_min]), py[k][h - csh[k]]) for k in range(n)])
         
        s.add([Or(Not(ph[h - h_min]), 
            Or([y[k][i] for i in range(h - csh[k] + 1)])) for k in range(n)])

        # Order encoding
        #if h < h_max - 1:
        #    s.add(Or(Not(ph[h - h_min]), ph[h - h_min + 1]))

    # --------------------------------------------------------------------
    # CHECK SAT
     
    for h in range(h_min, h_max):
        ss = copy.copy(s)
        ss.add(ph[h - h_min])
        #ss.add(ph[h_max - (h - h_min) - h_min - 1])
        
        if ss.check() == sat:
            m = ss.model()
            
            """
            l = [(i, j, m.evaluate(lr[i][j]), m.evaluate(lr[j][i]), m.evaluate(ud[i][j]), m.evaluate(ud[j][i]))
                for (i, j) in combinations(range(n), 2)]
            for i in range(len(l)):
                print("i: {}, j: {}, lr_ij: {}, lr_ji: {}, ud_ij: {}, ud_ji: {}"
                        .format(l[i][0], l[i][1], l[i][2], l[i][3], l[i][4], l[i][5]))
            """
            # x
            x_ev = [[m.evaluate(x[i][e]) for e in range(w - csw[i] + 1)] 
                    for i in range(n)]
            #print(x_ev)
            # y
            y_ev = [[m.evaluate(y[i][f]) for f in range(h_max - csh[i] + 1)]
                    for i in range(n)]
            #print(y_ev)
            # Evaluate height
            ph_ev = [m.evaluate(ph[hi - h_min]) for hi in range(h_min, h_max)]
            h_ev = ph_ev.index(True) + h_min
            
            plate.set_dim((w, h_ev))

            for k in range(n):
                xc, yc = x_ev[k].index(True), y_ev[k].index(True)
                print(xc, yc)
                plate.get_circuit(k).set_coordinate((xc, yc))
            return plate
        else:
            print("UNSAT, h: {}".format(h))
        
    return []
