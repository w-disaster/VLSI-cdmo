include "globals.mzn";

% PARAMS
int: n;
int: width;
set of int: CIRCUITS = 1..n;         %range macro

array[CIRCUITS] of int: w;
array[CIRCUITS] of int: h;

int: max_y = max(h);
int: cont_lower_bound = ceil(sum([w[i]*h[i] | i in CIRCUITS]) / width);
int: h_max = ceil(n * max(h) / floor(width/max(w)));

% VARS
var max(max_y,cont_lower_bound)..h_max: height;
array[CIRCUITS] of var 0..width - min(w): x;
array[CIRCUITS] of var 0..h_max - min(h): y;

% CONSTRAINTS
constraint cumulative(y, h, w, width);
constraint cumulative(x, w, h, height);

constraint diffn(x, y, w, h);
constraint forall(i in CIRCUITS) (x[i] + w[i] <= width /\ y[i] + h[i] <= height);

% SYMMETRY BREAKING
%array[CIRCUITS] of int: sort = reverse(arg_sort([w[i] | i in CIRCUITS])); alternative width-based
array[CIRCUITS] of int: sort = reverse(arg_sort([w[i]*h[i] | i in CIRCUITS]));

constraint symmetry_breaking_constraint(x[sort[1]]=0 /\ y[sort[1]]=0); %biggest chip in (0,0)
constraint symmetry_breaking_constraint(forall(i, j in sort) % no swaps between blocks with same w or different w but same h
  (if i>j
     then (if x[i] == x[j]
             then if w[i] == w[j]
                    then y[i] < y[j]
                  elseif h[i] == h[j]
                    then y[i] < y[j]
                  else true
                  endif
           endif)
   endif)        
);

% ROTATION HANDLING (we should use two different models: one with and one without rotation)
%array[CIRCUITS] of var 0..1: z;
%
%array[CIRCUITS] of var 0..max(width,h_max): rot_w = [h[i]*z[i]+w[i]*(1-z[i]) | i in CIRCUITS];
%array[CIRCUITS] of var 0..max(width,h_max): rot_h = [w[i]*z[i]+h[i]*(1-z[i]) | i in CIRCUITS];
%
%simply substitute w and h in every constraint with rot_w and rot_h


% SOLVER
solve :: seq_search([
         int_search([x[i] | i in sort], input_order, indomain_min, complete),
         int_search([y[i] | i in sort], input_order, indomain_min, complete)]) minimize height;

% OUTPUT
output ["\(width) \(height)\n" ++ "\(n)\n" ++ concat(["\(w[i]) \(h[i]) \(x[i]) \(y[i])\n" | i in CIRCUITS])];