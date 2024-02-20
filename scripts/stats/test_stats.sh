#!/bin/sh

all=""
for c1 in  "documente_1"
do

    all="$all test_corpora/$c1"
done

echo $all

python stats.py -c $all | tee stats_test.tsv

