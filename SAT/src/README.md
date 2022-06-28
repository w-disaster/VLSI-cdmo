# VLSI - SAT

Parameters: 
- width $w$
- $n$ number of blocks
- $B_i$ $i = 0, ..., n-1$ blocks to insert where $B_i = \{x_i, y_i\}$ are the dimensions of the $i$-block.

Constraints:

- The blocks in the grid can't overlap (exactly one value for each cell). $\sum_{k=0}^{n}(\texttt{cells}_{i,j,k}) \leq 1 \land \sum_{k=0}^{n}(\texttt{cells}_{i,j,k}) \geq 1$ $\forall i,j=0,...,n-1 $
- The cell $\texttt{cells}_{i, j}$ is the bottom left border of one block and its surrounding cells must have the same $k$ value. Moreover, inserting a block mustn't enlarge the width $w$. $\texttt{exactly-one} \Big[ \huge{\land_{\small r=i}^{\small i+y_k} \land_{\small c=j}^{\small j+x_k}}$ $\Big( \texttt{cells}_{r,c,k} \land (j + x\_k < w)  \land (i + y\_k < h) \Big)$ $\forall i,j=0,...,n-1 \Big]$ $\forall k=0,...,n$

Objective function:
- minimize the height of the I.C.
