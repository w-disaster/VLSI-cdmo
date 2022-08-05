from z3 import *
from itertools import combinations

def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name = ""):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one_np(bool_vars), And(at_most_one_np(bool_vars, name)))

def vlsi_sat_cells(n, b, w, rot=False):
    # - Each cell assumes a value between 0 and n (included), where the 0-value
    #        means that no block is inserted in that cell
    # - the height of the grid is the sum of the height of the blocks
    exactly_one = exactly_one_np    
    #b = [(1, 1)] + b
    h = sum([bh for (bw, bh) in b])
    # cells[i][j] : cell of row i and column j
    cells = [[[Bool(f"cells_{i}_{j}_{k}") for k in range(n + 1)] for j in range(w)] 
         for i in range(h)]
    #is_in_block = [[Bool(f"b_{i}_{j}") for j in range(w)] for i in range(h)]
    
    o = Optimize()
    # Each cell must contain a value only, corresponding to the block 
    # number e.g. the blocks can't overlap.
    for i in range(h):
        for j in range(w):
            o.add(exactly_one([cells[i][j][k] for k in range(n + 1)]))

    for k in range(n):
        (x, y) = b[k]
        cnst = []
        
        for i in range(h):
            for j in range(w):
                if j + x < w and i + y < h:
                    block = [cells[r][c][k] 
                             for r in range(i, i + y) for c in range(j, j + x)]
                    cnst.append(And(block))
                else:
                    cnst.append(False)
        o.add(exactly_one(cnst))
    
    #is_row_empty = [If(Sum([cells[i][j][k] for k in range(n) for j in range(w)]) > 0, 1, 0)
    #           for i in range(h)] 
    #max_empty_rows = Sum([is_row_empty[i] for i in range(h)])
    #o.maximize(max_empty_rows)
    
    o.maximize(Sum([cells[i][j][n] for i in range(h) for j in range(w)]))
    
    # Check if it's SAT
    o.check()
    if o.check() == sat:
        m = o.model()
        return [(i, j, k) for i in range(h) for j in range(w) 
                for k in range(n + 1) if m.evaluate(cells[i][j][k])]
    return "UNSAT"
