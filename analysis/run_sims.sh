#!/bin/bash
cd "$(dirname "$0")/.."
export GRF_THREADS=1
# replicate counts used in the revised manuscript
for s in B0:100 B1:30 B2:30 B3:30 B4:30 B5:30 B6:30 A1:5 A3:10 A4:5 A5:5 A6:10 A7:3; do
  sc=${s%%:*}; n=${s##*:}
  Rscript analysis/sim.R $sc 1 $n >> work/sim.log 2>&1
done
echo SIMDONE >> work/sim.log
