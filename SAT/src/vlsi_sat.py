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
    # - Each cell assumes a value between 0 and n (included), where the 0-value
    #        means that no block is inserted in that cell
    # - the height of the grid is the sum of the height of the blocks
    exactly_one = exactly_one_np    
    
    (n, (w,), cs) = (plate.get_n(), plate.get_dim(),
            plate.get_circuits())

    # Maximum height                            
    max_x = max([cs[i].get_dim()[0] for i in range(n)])
    max_y = max([cs[i].get_dim()[1] for i in range(n)])

    max_block_per_w = floor(w / max_x)                                           
    h_max = ceil(n * max_y / max_block_per_w) 

    # Z3 variables
    cells = [[[Bool(f"cells_{i}_{j}_{k}") for k in range(n + 1)] for j in range(w)] 
         for i in range(h_max)]
    h = Int(f"h")

    o = Optimize()
    o.add(And(h < h_max, h > max_y))

    # Each cell must contain a value only, corresponding to the block 
    # number e.g. the blocks can't overlap.
    for i in range(h_max):
        for j in range(w):
            o.add(exactly_one([cells[i][j][k] for k in range(n + 1)]))
      
    csx = [Int(f"x_{i}") for i in range(n)]
    csy = [Int(f"y_{i}") for i in range(n)]

    for k in range(n):
        (x, y) = (cs[k].get_dim()[0], cs[k].get_dim()[1])
        cnst = []
        
        for i in range(h_max):
            for j in range(w):
                if j + x <= w and i + y <= h_max:  
                    block = [cells[r][c][k] 
                             for r in range(i, i + y) for c in range(j, j + x)]
                    cnst.append(And(block))
                    o.add(Implies(And(block), And(csx[k] == j, csy[k] == i)))
                else:
                    cnst.append(False)
        o.add(exactly_one(cnst))

    o.add(h == z3_max([csy[i] + cs[i].get_dim()[1] for i in range(n)]))
    o.minimize(h)

    o.check()    
    if o.check() == sat:
        print("sat")
        
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
