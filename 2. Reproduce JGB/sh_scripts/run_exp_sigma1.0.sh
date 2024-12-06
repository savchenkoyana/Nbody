#!/bin/bash

echo "Generate coordinates for experiment: sigma=1.0"
python create_ic.py \
  --N 20000 \
  --mu 0 \
  --scale 1 \
  --sigma 1.0 \
  --plummer-r 10 \
  --n-iterations 20

echo
echo "Preprocess data:"
python preprocess_snap.py \
  --nemo-file snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

echo
echo "Start evolution for 13.7 Gyr for: sigma=1.0"
nice -n 20 gyrfalcON snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC_preprocessed.nemo \
  snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out.nemo \
  logstep=3000 \
  eps=0.0003684031498640387 \
  kmax=15 \
  tstop=14 \
  step=1.8693875619711035e-04 \
  Grav=4.30091727067736e-06
