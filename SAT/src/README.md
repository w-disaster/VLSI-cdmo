# VLSI - SAT

Parameters: 
- width $w$
- $n$ number of blocks
- $B_i$ $i = 0, ..., n-1$ blocks to insert where $B_i = \{x_i, y_i\}$ are the dimensions of the $i$-block.

Constraints:
- Inserting a block mustn't enlarge the width $w$
- Each cell must contain a value only, corresponding to the block number e.g. the blocks can't overlap.

- $\huge{\lor_{\small k=0}^{\small n-1}} \huge{\land_{\small r=i}^{\small i+y_k} \land_{\small c=j}^{\small j+x_k}}$ $\Big( \texttt{cll}_{r,c} = k \land (i+y_k < n) \land (j+x_k<n) \Big)$ $\forall i,j=0,...,n-1 $

Objective function:
- minimize the height of the I.C.
