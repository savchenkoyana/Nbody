#!/bin/bash
#
# Description: This script is used to compare N-body simulation methods on a small dataset.
#              Based on discussion in https://github.com/teuben/nemo/issues/170
# Usage: bash sh_scripts/run_fast_check.sh

rm -rf nbody0.in nbody0.out nbody1.out nbody2.out gyrfalcon.out

ETA=0.001
EPS=0.05

mkplummer nbody0.in 10 seed=123

nbody0 nbody0.in nbody0.out tcrit=10 deltat=0.01 eta=$ETA eps=$EPS
runbody1 nbody0.in nbody1.out tcrit=10 deltat=0.01 eta=$ETA eps=$EPS

runbody2 nbody0.in nbody2.out tcrit=10 deltat=0.01 etai=$ETA etar=2*$ETA eps=$EPS
u3tos nbody2.out/OUT3 nbody2.out/OUT3.snap

gyrfalcON nbody0.in gyrfalcon.out kmax=15 eps=$EPS tstop=10 step=0.01 theta=0.001 Ncrit=1

for i in $(seq 0 9); do
   echo "Particle $i"
   snapmask nbody0.out           - $i | snapplot - trak=t yapp=1/xs
   snapmask nbody1.out/OUT3.snap - $i | snapplot - trak=t yapp=2/xs
   snapmask nbody2.out/OUT3.snap - $i | snapplot - trak=t yapp=3/xs
   snapmask gyrfalcon.out        - $i | snapplot - trak=t yapp=4/xs
   echo -n "Enter to continue:"; read _
done
