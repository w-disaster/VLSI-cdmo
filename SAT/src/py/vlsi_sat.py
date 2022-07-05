#!/usr/bin/python3
from z3 import *
from itertools import combinations

def vlsi_sat(n, b, w, rot=False):
    # b = (bw, bh)
    # left bottom coordinates of each placed block
    x = [Int(f"x_{i}") for i in range(len(b))]
    y = [Int(f"y_{i}") for i in range(len(b))]
    h = Int(f"h")
        
    o = Optimize()
    
    hs = sum([bh for (bw, bh) in b])
    o.add(h < hs)
    
    # each block must be placed between 0 and w in the x-axis, 0 and h in the
    # y one.
    # x_i + bw_i < w and y_i + bh_i < h foreach i in [0, ..., len(b)]
    # x_i >= 0 and y_i >= 0 foreach i in [0, ..., len(b)]
    o.add([And(x[i] >= 0, x[i] + b[i][0] < w,
              y[i] >= 0, y[i] + b[i][1] < h) for i in range(len(b))])  

    # foreach pair of blocks: one must be placed before or next the other or
    # above or below
    o.add([Or(x[i] + b[i][0] <= x[j], x[j] + b[j][0] <= x[i],
        y[i] + b[i][1] <= y[j], y[j] + b[j][1] <= y[i])
         for (i, j) in combinations(range(len(b)), 2)])
       
    o.minimize(h)
    
    o.check()
    if o.check() == sat:
        m = o.model()
        return (m.evaluate(h).as_long(),
                [(m.evaluate(x[i]).as_long(), m.evaluate(y[i]).as_long())
                for i in range(len(b))])
    return ([], [])
