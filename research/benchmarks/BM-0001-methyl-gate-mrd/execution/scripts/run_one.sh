#!/bin/bash
# $1 job id  $2 bam  $3 candidates  $4 out  [$5 chrom filter]
cd /big8_disk/hung114/ONT_MRD/mrd/research/benchmarks/BM-0001-methyl-gate-mrd
extra=""
[ -n "$5" ] && extra="--chrom-filter $5"
start=$(date +%s)
python3 execution/scripts/run_sample.py --bam "$2" --candidates "$3" --out "$4" $extra \
    > "execution/logs/$1.out" 2> "execution/logs/$1.err"
rc=$?
echo -e "$1\t$rc\t$(( $(date +%s) - start ))\t$2\t$4" >> execution/logs/timings.tsv
exit $rc
