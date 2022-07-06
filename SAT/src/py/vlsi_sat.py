#!/usr/bin/python3
from z3 import *
from itertools import combinations

def vlsi_sat(n, b, w, rot):
    # b = (bw, bh)
    # left bottom coordinates of each placed block
    x = [Int(f"x_{i}") for i in range(len(b))]
    y = [Int(f"y_{i}") for i in range(len(b))]
    z = [Int(f"z_{i}") for i in range(len(b))]
    h = Int(f"h")
        
    o = Optimize()

    # Maximum height
    hs = sum([bh for (bw, bh) in b])
    o.add(And(h < hs, h > 0))

    rot = True
    # Set z to all zeros if rot == False
    if not rot:
        o.add(And([zz == 0 for zz in z]))
    else:
        o.add(And([Or(zz == 0, zz == 1) for zz in z]))

    # each block must be placed between 0 and w in the x-axis, 0 and h in the
    # y one.
    # x_i + bw_i < w and y_i + bh_i < h foreach i in [0, ..., len(b)]
    # x_i >= 0 and y_i >= 0 foreach i in [0, ..., len(b)]
    o.add([And(x[i] >= 0, x[i] + (z[i] * b[i][0]) + ((1 - z[i]) * b[i][1]) < w,
              y[i] >= 0, y[i] + (z[i] * b[i][1]) + ((1 - z[i]) * b[i][0]) < h) 
              for i in range(len(b))])  

    # foreach pair of blocks: one must be placed before or next the other or
    # above or below
    #o.add([Or(x[i] + b[i][0] <= x[j], x[j] + b[j][0] <= x[i],
    #    y[i] + b[i][1] <= y[j], y[j] + b[j][1] <= y[i])
    #     for (i, j) in combinations(range(len(b)), 2)])

    o.add([Or(
        x[i] + (z[i] * b[i][0]) + ((1 - z[i]) * b[i][1]) <= x[j],
        x[j] + (z[j] * b[j][0]) + ((1 - z[j]) * b[j][1]) <= x[i],
        
        y[i] + (z[i] * b[i][1]) + ((1 - z[i]) * b[i][0]) <= y[j],
        y[j] + (z[j] * b[j][1]) + ((1 - z[j]) * b[j][0]) <= y[i])
        for (i, j) in combinations(range(len(b)), 2)])
        
    o.minimize(h)
    
    o.check()
    if o.check() == sat:
        m = o.model()
        print([m.evaluate(z[i]) for i in range(len(b))])

        ret_eval = []
        h_ev = m.evaluate(h).as_long()
        for i in range(len(b)):
            x_ev, y_ev = m.evaluate(x[i]).as_long(), m.evaluate(y[i]).as_long()
        
            # [(x_start, x_end), (y_start, y_end)]
            z_ev = m.evaluate(z[i]).as_long()
            ret_eval.append((x_ev, x_ev + (z_ev * b[i][0]) + ((1 - z_ev) * b[i][1]), 
                y_ev, y_ev + (z_ev * b[i][1]) + ((1 - z_ev) * b[i][0])))
        
        return (h_ev, ret_eval)
    return ([], [])
