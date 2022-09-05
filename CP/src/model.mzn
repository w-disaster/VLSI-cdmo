include "globals.mzn";

% PARAMS
int: n;
int: w;
set of int: CIRCUITS = 1..n;         %range macro

array[CIRCUITS] of int: cw;
array[CIRCUITS] of int: ch;

int: max_y = max(ch);
int: cont_lower_bound = ceil(sum([cw[i] * ch[i] | i in CIRCUITS]) / w);
int: h_max = ceil(n * max(ch) / floor(w / max(cw)));

% VARS
var max(max_y,cont_lower_bound)..h_max: h;
array[CIRCUITS] of var 0..w - min(cw): x;
array[CIRCUITS] of var 0..h_max - min(ch): y;

% CONSTRAINTS
constraint cumulative(y, ch, cw, w);
constraint cumulative(x, cw, ch, h);

constraint diffn(x, y, cw, ch);
constraint forall(i in CIRCUITS) (x[i] + cw[i] <= w /\ y[i] + ch[i] <= h);

% SYMMETRY BREAKING
%array[CIRCUITS] of int: sort = reverse(arg_sort([w[i] | i in CIRCUITS])); alternative width-based
array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i] * ch[i] | i in CIRCUITS]));

constraint symmetry_breaking_constraint(x[sort[1]]=0 /\ y[sort[1]]=0); %biggest chip in (0,0)
constraint symmetry_breaking_constraint(forall(i, j in sort) % no swaps between blocks with same w or different w but same h
  (if i>j
     then (if x[i] == x[j]
             then if cw[i] == cw[j]
                    then y[i] < y[j]
                  elseif ch[i] == ch[j]
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
output ["\(w) \(h)\n" ++ "\(n)\n" ++ concat(["\(cw[i]) \(ch[i]) \(x[i]) \(y[i])\n" | i in CIRCUITS])];