#!/usr/bin/python3
from z3 import *
from utils import *
from itertools import combinations

def vlsi_sat(plate, rot=False):
    # b = (bw, bh)
    # left bottom coordinates of each placed block
    (n_circuits, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

    x = [Int(f"x_{i}") for i in range(n_circuits)]
    y = [Int(f"y_{i}") for i in range(n_circuits)]
    z = [Int(f"z_{i}") for i in range(n_circuits)]
    h = Int(f"h")
        
    o = Optimize()

    # Maximum height
    hs = sum([c.get_dim()[1] for c in cs])
    o.add(And(h < hs, h > 0))

    rot = True
    # Set z to all zeros if rot == False
    if not rot:
        o.add(And([z[i] == 1 for i in range(n_circuits)]))
    else:
        o.add(And([Or(z[i] == 0, z[i] == 1) for i in range(n_circuits)]))

    # each block must be placed between 0 and w in the x-axis, 0 and h in the
    # y one.
    # x_i + bw_i < w and y_i + bh_i < h foreach i in [0, ..., len(b)]
    # x_i >= 0 and y_i >= 0 foreach i in [0, ..., len(b)]
    print(n_circuits)
    o.add([And(x[i] >= 0, x[i] + (z[i] * cs[i].get_dim()[0]) + ((1 - z[i]) * cs[i].get_dim()[1]) < w,
              y[i] >= 0, y[i] + (z[i] * cs[i].get_dim()[1]) + ((1 - z[i]) * cs[i].get_dim()[0]) < h) 
              for i in range(n_circuits)])

    # foreach pair of blocks: one must be placed before or next the other or
    # above or below
    #o.add([Or(x[i] + b[i][0] <= x[j], x[j] + b[j][0] <= x[i],
    #    y[i] + b[i][1] <= y[j], y[j] + b[j][1] <= y[i])
    #     for (i, j) in combinations(range(len(b)), 2)])
    o.add([Or(
        x[i] + (z[i] * cs[i].get_dim()[0]) + ((1 - z[i]) * cs[i].get_dim()[1]) <= x[j],
        x[j] + (z[j] * cs[j].get_dim()[0]) + ((1 - z[j]) * cs[j].get_dim()[1]) <= x[i],
        
        y[i] + (z[i] * cs[i].get_dim()[1]) + ((1 - z[i]) * cs[i].get_dim()[0]) <= y[j],
        y[j] + (z[j] * cs[j].get_dim()[1]) + ((1 - z[j]) * cs[j].get_dim()[0]) <= y[i])
        for (i, j) in combinations(range(n_circuits), 2)])
        
    o.minimize(h)
    
    o.check()
    if o.check() == sat:
        m = o.model()
        print([m.evaluate(z[i]) for i in range(n_circuits)])

        # Set height of the plate
        h_ev = m.evaluate(h).as_long()
        plate.set_dim((w, h_ev))

        for i in range(n_circuits):
            x_ev, y_ev = m.evaluate(x[i]).as_long(), m.evaluate(y[i]).as_long()
            plate.get_circuit(i).set_coordinate((x_ev, y_ev))
        
            # Se == 0
            if m.evaluate(z[i]).as_long() == 0:
                (cw, ch) = plate.get_circuit(i).get_dim()
                plate.get_circuit(i).set_dim((ch, cw))

        return plate
    return []
