#!/usr/bin/python3
from minizinc import *#Instance, Model, Solver
from model.VLSISolver import *
from model.Plate import *
from math import floor, ceil
import numpy as np

class VLSI_CP(VLSISolver):
    def __init__(self, plate: Plate, rot=False):
        self.plate = plate
        (self.n, (self.w,), cs) = (plate.get_n(), plate.get_dim(), plate.get_circuits())
        self.rot = rot
        self.csw, self.csh = [], []
        for i in range(self.n):
            self.csw.append(cs[i].get_dim()[0])
            self.csh.append(cs[i].get_dim()[1])
       
    def compute_lower_upper_bound(self, csw, csh, w, n):                                                            
        max_x, max_y = max(csw), max(csh)
        max_block_per_w = floor(w / max_x)      
        h_max = ceil(n * max_y / max_block_per_w)
        h_min = max_y 
        return (h_min, h_max)

    def solve_vlsi(self) -> Plate:
        (self.h_min, self.h_max) = self.compute_lower_upper_bound(self.csw, 
                self.csh, self.w, self.n)

        #CP
        model = Model("model.mzn") if not self.rot else Model("model_rot.mzn")
        solver = Solver.lookup("chuffed")
        
        instance = Instance(solver, model)
        
        instance["w"] = self.w
        instance["n"] = self.n
        instance["cw"] = self.csw
        instance["ch"] = self.csh
        
        result = instance.solve()
        
        
        self.plate.set_dim((self.result["width"], result["height"]))
        for i in range(self.n):
            self.plate.get_circuit(i).set_coordinate((result['x['+i+']'], result['y['+i+']']))
        
        return self.plate
