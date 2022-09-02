#!/bin/bash

for I in {1..40} 
do
    ./vlsi_p1.py -i ../../instances/ins-${I}.txt -o prova.txt -r False &
done
