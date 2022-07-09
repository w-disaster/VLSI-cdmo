include "alldifferent.mzn";

int: n;
int: w;
array[1..n] of var 1..w: cw;
array[1..n] of int: ch;

var 1..sum(ch): h;

array[1..n] of var 1..w: x;
array[1..n] of var 1..sum(ch): y;
array[1..n] of var 0..1: z;

constraint forall (i in 1..n) (z[i] = 1);

constraint forall (i in 1..n) (x[i] > 0 /\ x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= w);
constraint forall (i in 1..n) (y[i] >= 0 /\ y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= h);

constraint forall (i,j in 1..n where i < j) (
                          x[i] + (z[i] * cw[i]) + ((1 - z[i]) * ch[i]) <= x[j] \/
                          x[j] + (z[j] * cw[j]) + ((1 - z[j]) * ch[j]) <= x[i] \/
                          
                          y[i] + (z[i] * ch[i]) + ((1 - z[i]) * cw[i]) <= y[j] \/
                          y[j] + (z[j] * ch[j]) + ((1 - z[j]) * cw[j]) <= y[i]);
                                 
solve minimize h;

output ["(w, h) = (\(w), \(h))\t x = \(x)\t y = \(y)\t z = \(z)\n"]