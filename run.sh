#!/bin/bash
set -x

python ./spreader.py "$@"

k=$1
h_size=$2
h_num=$3
inputFilename=dist-$k-superspreader-$h_size-$h_num.txt
outputFilename=dist-$k-superspreader-$h_size-$h_num-out.txt
awk '!a[$0]++' $inputFilename > $outputFilename