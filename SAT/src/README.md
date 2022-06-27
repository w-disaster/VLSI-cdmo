# VLSI - SAT

Parameters: 
- width $w$
- $n$ number of blocks
- $X_i$ $i = 0, ..., n-1$ blocks to insert where $X_i = \{x_i, y_i\}$ are the dimensions of the $i$-block.

Constraints:
- Inserting a block mustn't enlarge the width $w$
- Each cell must contain a value only, corresponding to the block number e.g. the blocks can't overlap.

Objective function:
- minimize the height of the I.C.
