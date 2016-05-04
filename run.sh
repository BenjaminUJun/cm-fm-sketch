#!/bin/bash
set -x

python ./spreader.py "$@"

k=$1
inputFilename=dist-$k-superspreader.txt
outputFilename=dist-$k-superspreader-out.txt
awk '!a[$0]++' $inputFilename > $outputFilename