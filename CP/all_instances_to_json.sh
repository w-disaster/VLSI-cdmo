#!/bin/bash

mkdir json_instances
for I in {1..40} 
do
    ./instance_to_json.py -i ../instances/ins-${I}.txt -o ./json_instances/ins-${I}.json
done
