#!/bin/bash
#
# Description: This script is used to compare N-body simulation methods on a small dataset.
#              Based on discussion in https://github.com/teuben/nemo/issues/170
# Usage: bash sh_scripts/run_fast_check.sh

rm -rf nbody0.in nbody0.out nbody1.in nbody2.in

mkplummer nbody0.in 10 seed=123

# default eta=0.02
nbody00 nbody0.in nbody0.out tcrit=10 deltat=0.01 eta=0.001
runbody1 nbody0.in nbody1.out tcrit=10 deltat=0.01 eta=0.001
runbody2 nbody0.in nbody2.out tcrit=10 deltat=0.01 etai=0.001 etar=0.002
u3tos nbody2.out/OUT3 nbody2.out/OUT3.snap

for i in $(seq 0 9); do
   echo "Particle $i"
   snapmask nbody0.out           - $i | snapplot - trak=t yapp=1/xs
   snapmask nbody1.out/OUT3.snap - $i | snapplot - trak=t yapp=2/xs
   snapmask nbody2.out/OUT3.snap - $i | snapplot - trak=t yapp=3/xs
   echo -n "Enter to continue:"; read _
done
