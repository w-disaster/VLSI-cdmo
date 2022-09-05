include "globals.mzn";

% PARAMS
int: n;
int: w;
set of int: CIRCUITS = 1..n; %range macro

array[CIRCUITS] of int: cw;
array[CIRCUITS] of int: ch;


int: max_y = max(ch);
int: cont_lower_bound = ceil(sum([cw[i] * ch[i] | i in CIRCUITS]) / w);
int: h_max = ceil(sum(ch) / floor(w / max(cw))) + 2;

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
array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i] | i in CIRCUITS])); %alternative w-based
%array[CIRCUITS] of int: sort = reverse(arg_sort([cw[i]*ch[i] | i in CIRCUITS]));

constraint symmetry_breaking_constraint(x[sort[1]] = 0 /\ y[sort[1]] = 0); %biggest chip in (0,0)
constraint symmetry_breaking_constraint(forall(i, j in sort) % no swaps between blocks with same w or different w but same h
 (if i>j
    then (if x[i] == x[j]
            then if cw[i] == cw[j]
                   then y[i] < y[j]
                 elseif ch[i] == ch[j]
                   then y[i] < y[j]
                 else true
                 endif
          %elseif y[i] == y[j]
          %  then if ch[i] == ch[j]
          %          then x[i] < x[j]
          %       elseif cw[i] == cw[j]
           %         then x[i] < x[j]
          %       else true
          %       endif
          %else true
          endif)
  endif)       
);

    %endif
    %elseif y[i] == y[j] then
    %  if ch[i] == ch[j] then
    %   x[i] < x[j]
    %  elseif cw[i] == cw[j] then
    %    x[i] < x[j]
    %  else 
    %    true
    %  endif
    %else
    %  true
    %endif
    %endif));                                                                                                       

%constraint forall(i, j in CIRCUITS where i < j)(cw[i] + cw[j] > w -> x[i] <= x[j] /\ x[j] <= x[i] + cw[i] \/
%                                                        x[j] <= x[i] /\ x[i] <= x[j] + cw[j]);
                                                        
%constraint forall(i, j in CIRCUITS where i < j)(ch[i] + ch[j] > h -> y[i] <= y[j] /\ y[j] <= y[i] + ch[i] \/
%                                                        y[j] <= y[i] /\ y[i] <= y[j] + ch[j]);
                                                       

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
%output ["\(w) \(h)\n" ++ "\(n)\n" ++ concat(["\(cw[i]) \(ch[i]) \(x[i]) \(y[i])\n" | i in CIRCUITS])];