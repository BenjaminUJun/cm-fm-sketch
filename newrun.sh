#!/bin/bash

for k in 10 20
do
    for h_size in 1000 2000
    do
        for h_num in 10 20
        do
            start=$SECONDS
            python ./spreader.py $k $h_size $h_num first_5k_src_dst second_5k_src_dst
            awk '!a[$0]++' dist-$k-superspreader-$h_size-$h_num.txt > dist-$k-superspreader-$h_size-$h_num-out.txt
            duration=$(( SECONDS - start ))
            echo "$k superspreader with $h_size and $h_num took $duration seconds" >> runlog
        done
    done
done