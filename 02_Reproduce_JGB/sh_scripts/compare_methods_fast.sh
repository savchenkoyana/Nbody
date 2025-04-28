#!/bin/bash
#
# Description: This script is used to compare N-body simulation methods on a small dataset.
#              Based on discussion in https://github.com/teuben/nemo/issues/170
# Usage: bash sh_scripts/compare_methods_fast.sh

rm -rf nbody0.in nbody0.out nbody1.out nbody2.out nbody4.out nbody6.out gyrfalcon.out
ETA=0.001
EPS=0.05
N=10

mkplummer nbody0.in $N seed=123

nbody0 nbody0.in nbody0.out tcrit=10 deltat=0.01 eta=$ETA eps=$EPS
runbody1 nbody0.in nbody1.out \
  tcrit=10 \
  deltat=0.01 \
  eta=$ETA \
  eps=$EPS \
  nbody=$N

runbody2 nbody0.in nbody2.out \
  tcrit=10 \
  deltat=0.01 \
  etai=$ETA \
  etar=2*$ETA \
  eps=$EPS \
  nbody=$N
u3tos nbody2.out/OUT3 nbody2.out/OUT3.snap mode=2

gyrfalcON nbody0.in gyrfalcon.out kmax=20 eps=$EPS tstop=10 step=0.01 theta=0.0001

runbody4 nbody0.in nbody4.out \
  tcrit=10 \
  deltat=0.01 \
  dtadj=0.01 \
  eta=$ETA \
  dtmin=1e-4 \
  rmin=1e-3 \
  q=0.5 \
  nbody=$N \
  kz=2,2,1,0,0,0,1,0,0,0,0,0,0,0,2,1,1,1,0,0,1,3,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0
# kz=0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,4
# kz=1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0

runbody6 nbody0.in nbody6.out \
  tcrit=10 \
  deltat=0.01 \
  dtadj=0.01 \
  etai=$ETA \
  etar=2*$ETA \
  dtmin=1e-4 \
  rmin=1e-3 \
  q=0.5 \
  nbody=$N \
  exe=nbody6 \
  nbody6=1 \
  kz=2,2,1,0,0,0,1,0,0,0,0,0,0,0,2,1,1,1,0,0,1,3,0,0,0,2,0,0,0,1,0,1,0,0,1,0,0,1,0,3,0,0,0,0,0,0,0,0,0,0
# kz=0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,5
# kz=1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0

for i in $(seq 1 10); do
  python plot_trajectory.py \
    --key $i \
    --files nbody0.out nbody1.out/OUT3.snap nbody2.out/OUT3.snap \
    nbody4.out/OUT3.snap nbody6.out/OUT3.snap gyrfalcon.out
done
