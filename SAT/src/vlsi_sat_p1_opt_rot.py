from z3 import *
from itertools import combinations
from math import floor, ceil
from copy import copy
import numpy as np

def vlsi_sat(plate, rot):
       
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())
    
    csw, csh = [], []
    for i in range(n):
        csw.append(cs[i].get_dim()[0])
        csh.append(cs[i].get_dim()[1])

    # Define upperbound and lowerbound                           
    max_x, max_y = max(csw), max(csh)

    if rot:
        max_block_per_w = floor(w / (max_x if max_x > max_y else max_y))
        h_max = ceil(sum([max(csh[i], csw[i]) for i in range(n)]) / max_block_per_w + 2)

    else:
        max_block_per_w = floor(w / max_x)                                           
        h_max = ceil(sum(csh) / max_block_per_w) + 2
    h_min = ceil(sum([csw[i] * csh[i] for i in range(n)]) / w) 
    
    # Z3 variables
    s = Solver()
    #s.set('timeout', 300 * 1000)

    px = [[Bool(f"px{i}_{e}") for e in range(w)] for i in range(n)]
    py = [[Bool(f"py{i}_{f}") for f in range(h_max)] for i in range(n)]
    z = [Bool(f"z_{i}") for i in range(n)] 
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

    # Rotation
    if not rot:
        s.add(And(z))
 
    # -------------------------------------------------------------------
    # NON-OVERLAPPING

    # Non-overlapping constraints
    s.add([Or(lr[i][j], lr[j][i], ud[i][j], ud[j][i]) 
        for (i, j) in combinations(range(n), 2)])
    import time
    start = time.time()
    for (i, j) in combinations(range(n), 2):
        # X-axis
        # (i, j)
        cx_ij = (And([Implies(lr[i][j], Not(px[j][k])) for k in range(csw[i])]), 
                And([Implies(lr[i][j], Not(px[j][k])) for k in range(csh[i])]))
        
        cx_ij_no = (And([Implies(And(lr[i][j], px[j][k + csw[i]]), px[i][k]) 
            for k in range(w - csw[i])]),
            (And([Implies(And(lr[i][j], px[j][k + csh[i]]), px[i][k]) 
            for k in range(w - csh[i])])))

        s.add(If(z[i], And(cx_ij[0], cx_ij_no[0]), And(cx_ij[1], cx_ij_no[1])))
        #s.add([Implies(And(lr[i][j], px[j][k + csw[i]]), px[i][k]) 
        #    for k in range(w - csw[i])])
        # (j, i)

        cx_ji = (And([Implies(lr[j][i], Not(px[i][k])) for k in range(csw[j])]), 
            And([Implies(lr[j][i], Not(px[i][k])) for k in range(csh[j])]))
        
        cx_ji_no = (And([Implies(And(lr[j][i], px[i][k + csw[j]]), px[j][k]) 
            for k in range(w - csw[j])]),
            (And([Implies(And(lr[j][i], px[i][k + csh[j]]), px[j][k]) 
            for k in range(w - csh[j])])))

        s.add(If(z[j], And(cx_ji[0], cx_ji_no[0]), And(cx_ji[1], cx_ji_no[1])))
        
        # Y-axis
        # (i, j)
        cy_ij = (And([Implies(ud[i][j], Not(py[j][k])) for k in range(csh[i])]), 
                And([Implies(ud[i][j], Not(py[j][k])) for k in range(csw[i])]))
        
        cy_ij_no = (And([Implies(And(ud[i][j], py[j][k + csh[i]]), py[i][k]) 
            for k in range(h_max - csh[i])]),
            (And([Implies(And(ud[i][j], py[j][k + csw[i]]), py[i][k]) 
            for k in range(h_max - csw[i])])))

        s.add(If(z[i], And(cy_ij[0], cy_ij_no[0]), And(cy_ij[1], cy_ij_no[1])))
        
         # (j, i)
        cy_ji = (And([Implies(ud[j][i], Not(py[i][k])) for k in range(csh[j])]), 
                And([Implies(ud[j][i], Not(py[i][k])) for k in range(csw[j])]))

        cy_ji_no = (And([Implies(And(ud[j][i], py[i][k + csh[j]]), py[j][k]) 
            for k in range(h_max - csh[j])]),
            (And([Implies(And(ud[j][i], py[i][k + csw[j]]), py[j][k]) 
            for k in range(h_max - csw[j])])))

        s.add(If(z[j], And(cy_ji[0], cy_ji_no[0]), And(cy_ji[1], cy_ji_no[1])))
        
        # C constraints
        #s.add(cx_ij[0] == cy_ij[0])
        #s.add(cx_ij[1] == cy_ij[1])
        #s.add(cx_ji[0] == cy_ji[0])
        #s.add(cx_ji[1] == cy_ji[1])
    print(time.time() - start)
    # Domain reduction     
    for i in range(n):
        # X-axis right border all True  
        s.add(If(z[i], And([px[i][e] for e in range(w - csw[i], w)]),
            And([px[i][e] for e in range(w - csh[i], w)])))

    # --------------------------------------------------------------
    # PLACE MAX AREA BLOCK
    m = np.argmax([csh[k] * csw[k] for k in range(n)]) 
    
    max_cx = (And([px[m][e] for e in range((w - csw[m]) // 2, w - csw[m])]), 
            And([px[m][e] for e in range((w - csh[m]) // 2, w - csh[m])]))
    max_cy = (And([py[m][e] for e in range((h_max - csh[m]) // 2, h_max - csh[m])]),
        And([py[m][e] for e in range((h_max - csw[m]) // 2, h_max - csw[m])]))

    s.add(If(z[m], And(max_cx[0], max_cy[0]), And(max_cx[1], max_cy[1])))

    # ----------------------------------------------------------------
    # REDUCING CONSTRAINTS 
    # X-axis 
    if rot:
        bs_x = [Implies(And(csw[i] > floor((w - csw[j]) / 2), 
            csw[i] > floor((w - csh[j]) / 2),
            csh[i] > floor((w - csw[j]) / 2),
            csh[i] > floor((w - csh[j]) / 2)), Not(lr[i][j]))
            for (i, j) in combinations(range(n), 2)] 
        bs_y = [Implies(And(csw[i] > floor((h_max - csw[j]) / 2), 
            csw[i] > floor((h_max - csh[j]) / 2),
            csh[i] > floor((h_max - csw[j]) / 2),
            csh[i] > floor((h_max - csh[j]) / 2)), Not(ud[i][j]))
            for (i, j) in combinations(range(n), 2)] 
         
    else:
        bs_x = [Implies(csw[i] > floor((w - csw[j]) / 2), Not(lr[i][j]))
                for (i, j) in combinations(range(n), 2)]
        bs_y = [Implies(csh[i] > floor((h_max - csh[j]) / 2), Not(ud[i][j])) 
            for (i, j) in combinations(range(n), 2)]
    
    s.add(And(bs_x), And(bs_y))

    # Y-axis
    if rot:
        bs_x = [Implies(And(csw[i] + csw[j] > w,
                            csh[i] + csw[j] > w,
                            csw[i] + csh[j] > w,
                            csh[i] + csh[j] > w), And(Not(lr[i][j]), Not(lr[j][i])))
                            for (i, j) in combinations(range(n), 2)]
        
        bs_y = [Implies(And(csw[i] + csw[j] > h_max,
                            csh[i] + csw[j] > h_max,
                            csw[i] + csh[j] > h_max,
                            csh[i] + csh[j] > h_max), And(Not(ud[i][j]), Not(ud[j][i])))
                            for (i, j) in combinations(range(n), 2)]

    else:
        bs_x = [Implies(csw[i] + csw[j] > w, And(Not(lr[i][j]), Not(lr[j][i])))
                for (i, j) in combinations(range(n), 2)]
        bs_y = [Implies(csh[i] + csh[j] > h_max, And(Not(ud[i][j]), Not(ud[j][i])))
                for (i, j) in combinations(range(n), 2)]

    s.add(And(bs_x), And(bs_y))

    s.add([Implies(And(csw[i] == csw[j], csh[i] == csh[j]), 
        And(Not(lr[j][i]), Or(lr[i][j], Not(ud[j][i])))) for (i, j) in combinations(range(n), 2)])
     
    # Constraints    
    for h in range(h_min, h_max):
        s.add([Or(Not(ph[h - h_min]), 
            Or([py[k][i] for i in range(h - csh[k] + 1)])) for k in range(n)])
        
        hc = And([If(z[k], And([py[k][i] for i in range(h - csh[k], h_max)]),
            And([py[k][i] for i in range(h - csw[k], h_max)])) for k in range(n)])
        s.add(Implies(ph[h - h_min], hc))

        # Order encoding
        if h < h_max - 1: 
            s.add(Or(Not(ph[h - h_min]), ph[h - h_min + 1]))
   
    print("Evaluate step")
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
            x_ev = [[m.evaluate(px[i][e], model_completion=True) 
                for e in range(len(px[i]))] for i in range(len(px))]
            y_ev = [[m.evaluate(py[i][f], model_completion=True) 
                for f in range(len(py[i]))] for i in range(len(py))]
            z_ev = [m.evaluate(z[i], model_completion=True) for i in range(n)]
            
            print(z_ev)
            plate.set_dim((w, h))
            for k in range(n):
                xc, yc = x_ev[k].index(True), y_ev[k].index(True)
                plate.get_circuit(k).set_coordinate((xc, yc))                
                if not z_ev[k]:
                    dim = plate.get_circuit(k).get_dim()
                    plate.get_circuit(k).set_dim((dim[1], dim[0]))

            last_plate = copy(plate)
            ub = h
        else:
            print("UNSAT, h: {}".format(h))
            lb = h

        h = floor((ub + lb) / 2)
    return last_plate
