include "globals.mzn";

% PARAMS
int: n;
int: w;
set of int: CIRCUITS = 1..n; %range macro

array[CIRCUITS] of int: cw;
array[CIRCUITS] of int: ch;
array[CIRCUITS] of var bool: z;

int: max_y = max(max(ch), max(cw));%min(max(ch), max(cw));
int: cont_lower_bound = ceil(sum([cw[i] * ch[i] | i in CIRCUITS]) / w);
int: h_max = ceil(n * max_y / floor(w / max(cw)));

% VARS
var max(max_y, cont_lower_bound)..h_max: h;
array[CIRCUITS] of var 0..w - min(min(cw), min(ch)): x;
array[CIRCUITS] of var 0..h_max - min(min(cw), min(ch)): y;

% CONSTRAINTS
constraint cumulative(y, [if z[i] then ch[i] else cw[i] endif | i in CIRCUITS], 
                         [if z[i] then cw[i] else ch[i] endif | i in CIRCUITS], w);
constraint cumulative(x, [if z[i] then cw[i] else ch[i] endif | i in CIRCUITS],
                         [if z[i] then ch[i] else cw[i] endif | i in CIRCUITS], h);

constraint diffn(x, y, cw, ch);
constraint forall(i in CIRCUITS) (x[i] + z[i] * cw[i] + (1 - z[i]) * ch[i] <= w /\ 
                                  y[i] + z[i] * ch[i] + (1 - z[i]) * cw[i] <= h);

% SYMMETRY BREAKING
array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i] | i in CIRCUITS])); %alternative w-based
%array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i]*ch[i] | i in CIRCUITS]));

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
          endif
         )
  endif)       
);

constraint forall(i, j in CIRCUITS)(ch[i] + ch[j] > h -> y[i] <= y[j] + ch[j]);

% ROTATION HANDLING (we should use two different models: one with and one without rotation)
%array[CIRCUITS] of var 0..1: z;
%
%array[CIRCUITS] of var 0..max(w,h_max): rot_w = [ch[i]*z[i]+cw[i]*(1-z[i]) | i in CIRCUITS];
%array[CIRCUITS] of var 0..max(w,h_max): rot_h = [cw[i]*z[i]+ch[i]*(1-z[i]) | i in CIRCUITS];
%
%simply substitute w and h in every constraint with rot_w and rot_h


% SOLVER
solve :: seq_search([
        int_search([x[i] | i in sort], input_order, indomain_min, complete),
        int_search([y[i] | i in sort], input_order, indomain_min, complete)]) minimize h;


% OUTPUT
output ["\(w) \(h)\n" ++ "\(n)\n" ++ concat(["\(cw[i]) \(ch[i]) \(x[i]) \(y[i]) \t\(z[i])\n" | i in CIRCUITS])];
