#!/bin/bash
cd "$(dirname "$0")/.."
export GRF_THREADS=1 GRF_TREES=2000
Rscript analysis/boot.R $1 $2 >> work/boot.log 2>&1
echo BOOTDONE $1 $2 >> work/boot.log
