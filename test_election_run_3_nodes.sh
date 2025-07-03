#!/bin/sh

SCRIPT="main.py --id"

for i in 1 2 3; do
    python3 $SCRIPT $i &
done 

