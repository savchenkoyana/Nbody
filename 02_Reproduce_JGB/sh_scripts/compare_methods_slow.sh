#!/bin/bash

echo "This script is used to run full simulation with variuos N-body methods"
echo "Usage: bash sh_scripts/compare_methods_slow.sh <N> <TASK> <ETA>"
echo
echo "<N> should be one of: 1000, 2000, 5000, 10000"
echo "<TASK> should be:"
echo "0 --- to create IC;"
echo "1 --- to run nbody0;"
echo "2 --- to run runbody1;"
echo "3 --- to run runbody2;"
echo "Choose <ETA> carefully (default value is 0.02)"
echo

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Wrong number of arguments!"
    exit 1
fi

N=$1
TASK=$2
ETA="${3:-0.001}"
ETAR=2*$ETA

if [[ $N == 1000 ]]; then
   EPS=0.001
elif [[ $N == 2000 ]]; then
   EPS=0.00079
elif [[ $N == 5000 ]]; then
   EPS=0.00058
elif [[ $N == 10000 ]]; then
   EPS=0.00046
else
   echo "Invalid N=$N! Choose one of: 1000, 5000, 10000"
   exit 1
fi

NPART=$N+1
DIR="snap_mu0.0_s1.0_sigma1.5_r10.0_N${N}"
IC_NBODY="${DIR}/IC_preprocessed_nbody.nemo"

if [[ $TASK -eq 0 ]]; then
  echo "Creating IC"

  python create_ic.py \
    --N $N \
    --mu 0 \
    --scale 1 \
    --sigma 1.5 \
    --plummer-r 10 \
    --n-iterations 20

  python preprocess_snap.py \
    --nemo-file $DIR/IC.nemo \
    --r-shift 34 0 0 \
    --v-shift 0 -74.35014 0 \
    --plummer-r 10 \
    --add-point-source \
    --source-mass 4.37e10

  snapscale in=$DIR/IC_preprocessed.nemo \
    out=$IC_NBODY \
    mscale=4.300451321727918e-06

elif [[ $TASK -eq 1 ]]; then
  echo "Running nbody0"

  # Nbody0
  time nice -n 20 nbody0 \
    $IC_NBODY \
    $DIR/out_nbody0.nemo \
    tcrit=14 \
    deltat=0.01 \
    eps=$EPS \
    eta=$ETA

  python postprocess_snap.py \
    --snap-file $DIR/out_nbody0.nemo \
    --remove-point-source \
    --nbody

elif [[ $TASK -eq 2 ]]; then
  echo "Running runbody1"

  # Nbody1
  time nice -n 20 runbody1 \
    in=$IC_NBODY \
    deltat=0.1 \
    tcrit=14 \
    nbody=$NPART \
    eps=$EPS \
    eta=$ETA \
    KZ6=0 \
    outdir=$DIR/runbody1

  python postprocess_snap.py \
    --snap-file $DIR/runbody1/OUT3.snap \
    --remove-point-source \
    --nbody

elif [[ $TASK -eq 3 ]]; then
  echo "Running runbody2"

  # Nbody2
  time nice -n 20 runbody2 \
    in=$IC_NBODY \
    deltat=0.1 \
    tcrit=14 \
    nbody=$NPART \
    eps=$EPS \
    etai=$ETA \
    etar=$ETAR \
    KZ6=0 \
    outdir=$DIR/runbody2

  u3tos $DIR/runbody2/OUT3 \
    $DIR/runbody2/OUT3.snap

  python postprocess_snap.py \
    --snap-file $DIR/runbody2/OUT3.snap \
    --remove-point-source \
    --nbody
fi
