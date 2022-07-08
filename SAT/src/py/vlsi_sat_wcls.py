#!/usr/bin/python3
from z3 import *
from model.Circuit import *
from model.Plate import *
from itertools import combinations

def vlsi_sat(plate, rot=False):
    # b = (bw, bh)
    # left bottom coordinates of each placed block
    (n_circuits, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

    (cw, ch) = ([cs[i].get_dim()[0] for i in range(n_circuits)],
        [cs[i].get_dim()[1] for i in range(n_circuits)])

    x = [Int(f"x_{i}") for i in range(n_circuits)]
    y = [Int(f"y_{i}") for i in range(n_circuits)]
    z = [Int(f"z_{i}") for i in range(n_circuits)]
    h = Int(f"h")
        
    o = Optimize()

    # Maximum height
    hs = sum(ch)
    o.add(And(h < hs, h > 0))

    # Set z to all 1s if rot == False
    if not rot:
        o.add(And([z[i] == 1 for i in range(n_circuits)]))
    else:
        o.add(And([Or(z[i] == 0, z[i] == 1) for i in range(n_circuits)]))

    # each block must be placed between 0 and w in the x-axis, 0 and h in the
    # y one.
    # x_i + bw_i < w and y_i + bh_i < h foreach i in [0, ..., len(b)]
    # x_i >= 0 and y_i >= 0 foreach i in [0, ..., len(b)]
    o.add([And(x[i] >= 0, x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) < w,
          y[i] >= 0, y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) < h) 
          for i in range(n_circuits)])

    # foreach pair of blocks: one must be placed before or next the other or
    # above or below
    o.add([Or(
        # x-axis constraints
        x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j],
        x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i],
        # y-axis constraints
        y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j],
        y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i])
        for (i, j) in combinations(range(n_circuits), 2)])
        
    o.minimize(h)
    
    o.check()
    if o.check() == sat:
        m = o.model()

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
