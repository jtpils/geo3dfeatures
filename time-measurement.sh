#!/bin/bash

# Run a set of experiments on feature generation,
# to measure the impact of point quantity, neighborhood size, and feature set.
# /!\ This program supposes to be inside the project virtual env

set -e
set -u

if [ "$#" -ne 4 ]; then
    echo "Wrong number of parameters. The command must be run as follows:"
    echo "./time-measurement.sh [experiment name] [point quantity] [neighborhood size] [feature set]"
    exit 1
fi

echo "Run time profiler on examples/example.py"
echo "Experiment name: $1"
echo "Numbers of evaluated points: $2"
echo "Sizes of neighborhoods: $3"
echo "Feature sets: $4"

xp_name=$1
mkdir -p data/profiling/$xp_name/profiling
mkdir -p data/profiling/$xp_name/out
mkdir -p data/profiling/$xp_name/timers

for points in $2 # '1000 5000 10000 50000'
do
    for neighbors in $3 # '20 50 100'
    do
	for feature_set in $4 # 'alphabeta eigenvalues full'
	do
	    echo "Run examples/example.py with $points points, $neighbors neighbors and the $feature_set feature set..."
	    _output_file="data/profiling/$xp_name/out/features-$points-$neighbors-$feature_set.csv"
	    _profiling_file="data/profiling/$xp_name/profiling/profiling-$points-$neighbors-$feature_set"
	    python -m cProfile -o $_profiling_file examples/example.py -i data/scene.xyz --output-file $_output_file -p $points -n $neighbors -t 1000 -f $feature_set
	    echo "**********"
	done
    done
done