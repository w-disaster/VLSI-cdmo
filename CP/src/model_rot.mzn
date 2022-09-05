include "globals.mzn";

% PARAMS
int: n;
int: w;
set of int: CIRCUITS = 1..n;

array[CIRCUITS] of int: cw;
array[CIRCUITS] of int: ch;

int: max_y = max(ch);
int: cont_lower_bound = ceil(sum([cw[i] * ch[i] | i in CIRCUITS]) / w);
int: h_max = ceil(n * max(ch) / floor(w / max(cw)));

% VARS
var max(max_y,cont_lower_bound)..h_max: h;
array[CIRCUITS] of var 0..w - min(cw): x;
array[CIRCUITS] of var 0..h_max - min(ch): y;

% ROTATION HANDLING
array[CIRCUITS] of var 0..1: z;

array[CIRCUITS] of var 0..max(w,h_max): rot_w = [ch[i] * z[i] + cw[i] * (1 - z[i]) | i in CIRCUITS];
array[CIRCUITS] of var 0..max(w,h_max): rot_h = [cw[i] * z[i] + ch[i] * (1 - z[i]) | i in CIRCUITS];

% CONSTRAINTS
constraint cumulative(y, rot_h, rot_w, w);
constraint cumulative(x, rot_w, rot_h, h);

constraint diffn(x, y, rot_w, rot_h);
constraint forall(i in CIRCUITS) (x[i] + rot_w[i] <= w /\ y[i] + rot_h[i] <= h);

% SYMMETRY BREAKING
array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i] * ch[i] | i in CIRCUITS]));

constraint symmetry_breaking_constraint(x[sort[1]]=0 /\ y[sort[1]]=0); %biggest chip in (0,0)
constraint symmetry_breaking_constraint(forall(i, j in sort) % no swaps between blocks with same w or different w but same h
  (if i>j
     then (if x[i] == x[j]
             then if rot_w[i] == rot_w[j]
                    then y[i] < y[j]
                  elseif rot_h[i] == rot_h[j]
                    then y[i] < y[j]
                  else true
                  endif
           endif)
   endif)        
);

% SOLVER
solve :: seq_search([
         int_search([x[i] | i in sort], input_order, indomain_min, complete),
         int_search([y[i] | i in sort], input_order, indomain_min, complete)]) minimize h;

% OUTPUT
output ["\(h)\n" ++ concat(["\(rot_w[i]) \(rot_h[i]) \(x[i]) \(y[i])\n" | i in CIRCUITS])];