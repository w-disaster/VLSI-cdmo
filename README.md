# VLSI Design
## Combinatorial decision making and optimization project by Luca Fabri and Giuseppe Morgese

VLSI (Very Large Scale Integration) refers to the trend of integrating circuits into silicon chips. 
A typical example is the smartphone. The modern trend of shrinking transistor sizes, 
allowing engineers to fit more and more transistors into the same area of silicon, has pushed the integration of
more and more functions of cellphone circuitry into a single silicon die (i.e.
plate).

As the combinatorial decision and optimization expert, the student is
assigned to design the VLSI of the circuits defining their electrical device:
given a fixed-width plate and a list of rectangular circuits, decide how to
place them on the plate so that the length of the final device is minimized.

The purpose of this project is to model and solve the chosen problem using
(i) Constraint Programming (CP), (ii) propositional SATisfiability (SAT)
and/or its extension to Satisfiability Modulo Theories (SMT), and (iii)
Mixed-Integer Linear Programming (MIP).

Each subdirectory contains a ```src``` directory, a ```README``` file with the specifications on
how to run the solver and a report, which describes the modeling and developing phases done
by the project members.

- The SAT subpart was implemented using the the [Z3](https://github.com/Z3Prover/z3) Python API, an high performance theorem prover
- CP was written using [Minizinc](https://www.minizinc.org/), a constraint programming language
- LP was developed using [PuLP](https://pypi.org/project/PuLP/), an LP modeler written in Python, which makes use of [CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) solver.
