#!/bin/bash

for i in {5000..5049}
do
   echo "Starting miner on port $i"
   python3 main.py $i &
   sleep 1  # Sleep for a second to avoid race conditions
done
