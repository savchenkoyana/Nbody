#!/bin/bash

echo "Generate coordinates for experiment: sigma=1.5"
python create_ic.py \
  --N 20000 \
  --mu 0 \
  --scale 1 \
  --sigma 1.5 \
  --plummer-r 10 \
  --n-iterations 20

echo
echo "Preprocess data:"
python preprocess_snap.py \
  --nemo-file snap_mu0.0_s1.0_sigma1.5_r10.0_N20000/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

echo
echo "Start evolution for 100 dynamical times for: sigma=1.5"
gyrfalcON snap_mu0.0_s1.0_sigma1.5_r10.0_N20000/IC_preprocessed.nemo \
  snap_mu0.0_s1.0_sigma1.5_r10.0_N20000/out.nemo \
  logstep=300 \
  eps=0.0003684031498640387 \
  kmax=15 \
  tstop=0.13757534452751557 \
  step=1.3757534452751556e-05 \
  Grav=4.30091727067736e-06
