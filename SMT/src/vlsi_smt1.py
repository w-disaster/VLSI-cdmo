#!/usr/bin/python3
from z3 import *
from model.Circuit import *
from model.Plate import *
from itertools import combinations
from math import floor, ceil

def vlsi_smt(plate, rot=False):
    # b = (bw, bh)
    # left bottom coordinates of each placed block
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

    x, y, z = [], [], []
    cw, ch = [], []
    h = Int(f"h")
    for i in range(n):
        x.append(Int(f"x_{i}"))
        y.append(Int(f"y_{i}"))
        z.append(Int(f"z_{i}"))
                
        cw.append(cs[i].get_dim()[0])
        ch.append(cs[i].get_dim()[1])

    # Optimize
    o = Optimize()

    # Maximum height                            
    max_x = max([cs[i].get_dim()[0] for i in range(n)])
    max_y = max([cs[i].get_dim()[1] for i in range(n)])
    max_block_per_w = floor(w / max_x)                                           
    h_max = ceil(n * max_y / max_block_per_w)
    o.add(And(h < h_max, h > max_y))
    
       # Set z to all 1s if rot == False
    if not rot:
        o.add(And([z[i] == 1 for i in range(n)]))
    else:
        o.add(And([Or(z[i] == 0, z[i] == 1) for i in range(n)]))

    # each block must be placed between 0 and w in the x-axis, 0 and h in the
    # y one.
    # x_i + bw_i < w and y_i + bh_i < h foreach i in [0, ..., len(b)]
    # x_i >= 0 and y_i >= 0 foreach i in [0, ..., len(b)]
    o.add([And(x[i] >= 0, x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) - 1 < w,
          y[i] >= 0, y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) - 1 < h) 
          for i in range(n)])

    '''
    for (i, j) in combinations(range(n), 2):
        lr_ji = x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i]
        ud_ij = y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j]
        ud_ji = y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i]

        if cw[i] > floor((w - cw[j]) / 2):
            o.add(Or(lr_ji, ud_ij, ud_ji))
        else:
            lr_ij = x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j]
            o.add(Or(lr_ij, lr_ji, ud_ij, ud_ji))
    '''
    '''
    for (i, j) in combinations(range(n), 2):
        lr_ij = x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j]
        lr_ji = x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i]
        ud_ij = y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j]
        ud_ji = y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i]

        if not rot:
            if cw[i] + cw[j] > w:
                o.add(Or(ud_ij, ud_ji))
            else:
                o.add(Or(lr_ij, lr_ji, ud_ij, ud_ji))
        else:
            c = []
            if cw[i] + cw[j] > w:
                c.append(Not(And(z[i], z[j])))
            if cw[i] + ch[j] > w:
                c.append(Not(And(z[i], Not(z[j]))))
            if ch[i] + cw[j] > w:
                c.append(Not(And(Not(z[i]), z[j])))
            if ch[i] + ch[j] > w:
                c.append(Or(z[i], z[j]))

            o.add(c)
            o.add(lr_ij, lr_ji, ud_ij, ud_ji)
    '''
    # foreach pair of blocks: one must be placed before or next the other or
    # above or below
        
    o.add([Or(
        # x-axis constraints
        Or(
            x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j],
            x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i]),
        # y-axis constraints
        Or(
            y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j],
            y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i]))
        for (i, j) in combinations(range(n), 2)])

#    index = np.argmax(np.asarray(ch))
#    o.add(And(x[index] == 0, y[index] == 0))

    o.minimize(h)
    
    o.check()
    if o.check() == sat:
        m = o.model()

        # Set height of the plate
        h_ev = m.evaluate(h).as_long()
        plate.set_dim((w, h_ev))

        for i in range(n):
            x_ev, y_ev = m.evaluate(x[i]).as_long(), m.evaluate(y[i]).as_long()
            plate.get_circuit(i).set_coordinate((x_ev, y_ev))
            print(x_ev, y_ev)        
            # Se == 0
            if m.evaluate(z[i]).as_long() == 0:
                (cw, ch) = plate.get_circuit(i).get_dim()
                plate.get_circuit(i).set_dim((ch, cw))

        return plate
    return []