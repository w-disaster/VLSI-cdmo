from z3 import *
from itertools import combinations
from math import floor, ceil

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
    h_max = ceil(n * max_y / max_block_per_w) 
    h_min = max_y

    # Z3 Optimize
    o = Optimize()
    
    # -------------------------------------------------------------------
    # ORDER ENCODING

    # Z3 order encoding variables
    px = [[Bool(f"px{i}_{e}") for e in range(w - csw[i])]
        for i in range(n)]
    py = [[Bool(f"py{i}_{f}") for f in range(h_max - csh[i])]
        for i in range(n)]
    
    # Order encoding constraints
    for i in range(n):
        o.add([Implies(px[i][c], px[i][c + 1]) 
            for c in range(w - csw[i] - 1)])
        o.add([Implies(py[i][c], py[i][c + 1]) 
            for c in range(h_max - csh[i] - 1)])
        
    # -------------------------------------------------------------------
    # NON-OVERLAPPING

    # Non-overlapping variables
    lr = [[Bool(f"lr_{i}_{j}") for i in range(n)] for j in range(n)]
    ud = [[Bool(f"ud_{i}_{j}") for i in range(n)] for j in range(n)]

    # Non-overlapping constraints
    o.add([Or(Or(lr[i][j], lr[j][i]), Or(ud[i][j], ud[j][i])) 
        for i in range(n) for j in range(n)])

    for i in range(n):
        for j in range(i, n):
            
            for e in range(w - cs[j].get_dim()[0]]):
                # (lr_{i, j}, px_{j, e + w_i}) --> px_{i, e}
                o.add(Or(Not(lr[i][j]), px[i][e], Not(px[j][e + csw[i]])))
                # (lr_{j, i}, px_{i, e + w_j}) --> px_{j, e}
                o.add(Or(Not(lr[j][i]), px[j][e], Not(px[i][e + csw[j]])))
            
            for f in range(h_max - cs[i].get_dim()[1]]):
                # (ud_{i, j}, py_{j, f + h_i}) --> py_{i, h}
                o.add(Or(Not(ud[i][j]), px[i][f], Not(px[j][f + csh[i]]))) 
                # (ud_{j, i}, py_{i, f + h_j}) --> py_{j, h}
                o.add(Or(Not(lr[j][i]), px[j][f], Not(px[j][f + csh[j]])))
    
    # --------------------------------------------------------------------
    # CHECK SAT

    o.check()    
    if o.check() == sat:
        print("SAT")
        m = o.model()
        # Set height of the plate
        h_ev = m.evaluate(h).as_long()
        plate.set_dim((w, h_ev))

        for i in range(n):
            x_ev, y_ev = m.evaluate(csx[i]).as_long(), m.evaluate(csy[i]).as_long()
            print(x_ev, y_ev)
            plate.get_circuit(i).set_coordinate((x_ev, y_ev))
            # Se == 0
            #if m.evaluate(z[i]).as_long() == 0:
            #    (cw, ch) = plate.get_circuit(i).get_dim()
            #    plate.get_circuit(i).set_dim((ch, cw))   
        return plate
        
    print("unsat")
    return []
