#!/bin/bash

for (( i=1; i<=$1; i++))
do
    vec=$(./generate_poly.py)
    echo $vec
    #echo $( echo $vec | ./rfan)
done
