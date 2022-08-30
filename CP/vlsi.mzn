include "alldifferent.mzn";

int: n;
int: w;
array[0..n - 1] of var 1..w: cw;
array[0..n - 1] of int: ch;
bool: rot;

var 1..sum(ch): h;

array[0..n - 1] of var 0..w - 1: x;
array[0..n - 1] of var 0..sum(ch) - 1: y;
array[0..n - 1] of var 0..1: z;

array[0..n - 1, 0..n - 1] of var bool: lr;
array[0..n - 1, 0..n - 1] of var bool: ud;

constraint forall (i in 0..n - 1) (if not rot then z[i] = 1 endif);

constraint forall (i in 0..n - 1) (x[i] >= 0 /\ x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) - 1 < w);
constraint forall (i in 0..n - 1) (y[i] >= 0 /\ y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) - 1 < h);

constraint forall (i, j in 0..n - 1 where i < j) (
            lr[i, j] = (x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j]) /\
            lr[j, i] = (x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i]) /\
            ud[i, j] = (y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j]) /\
            ud[j, i] = (y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i]));

% Non-overlapping constraints
constraint forall (i, j in 0..n - 1 where i < j) (lr[i, j] \/ lr[j, i] \/ ud[i, j] \/ ud[j, i]);
                          
% Reduce search space excluding circuits which can't be put 
% one next to the other or one at the top of the other                            
constraint forall (i, j in 0..n where i < j) (
           cw[i] + cw[i] > w -> (not lr[i, j] /\ not lr[j, i]) /\
           ch[i] + ch[i] > h -> (not ud[i, j] /\ not ud[j, i]));

solve minimize h;                             

output ["(w, h) = (\(w), \(h)) \t x = \(x)\t y = \(y)\t z = \(z)\n"]