#!/bin/bash
#
# Description: This script is used to compare N-body simulation methods on a small dataset.
#              Based on discussion in https://github.com/teuben/nemo/issues/170
# Usage: bash sh_scripts/run_fast_check.sh

rm -rf nbody0.in nbody0.out nbody1.out nbody2.out gyrfalcon.out

# Peter Teuben used N=10, ETA=0.001 for tests
# However, I found that even ETA=0.01 is good (tested with N=1000)
# While default ETA=0.02 gives slightly different trajectories
ETA=0.001
EPS=0.05
N=10

mkplummer nbody0.in $N seed=123

nbody0 nbody0.in nbody0.out tcrit=10 deltat=0.01 eta=$ETA eps=$EPS
runbody1 nbody0.in nbody1.out tcrit=10 deltat=0.01 eta=$ETA eps=$EPS

runbody2 nbody0.in nbody2.out tcrit=10 deltat=0.01 etai=$ETA etar=2*$ETA eps=$EPS
u3tos nbody2.out/OUT3 nbody2.out/OUT3.snap mode=2

gyrfalcON nbody0.in gyrfalcon.out kmax=20 eps=$EPS tstop=10 step=0.01 theta=0.0001 Ncrit=1

runbody4 nbody0.in nbody4.out tcrit=10 deltat=0.01 eta=$ETA eps=0
u3tos nbody4.out/OUT3 nbody4.out/OUT3.snap mode=4

for i in $(seq 0 9); do
   echo "Particle $i"
   snapmask nbody0.out           - $i | snapplot - trak=t yapp=1/xs
   snapmask nbody1.out/OUT3.snap - $i | snapplot - trak=t yapp=2/xs
   snapmask nbody2.out/OUT3.snap - $i | snapplot - trak=t yapp=3/xs
   snapmask nbody4.out/OUT3.snap - $i | snapplot - trak=t yapp=4/xs
   snapmask gyrfalcon.out        - $i | snapplot - trak=t yapp=5/xs
   echo -n "Enter to continue:"; read _
done
