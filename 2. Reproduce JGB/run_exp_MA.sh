#!/bin/bash

echo "Generate coordinates for experiment: M&A"
python create_ic.py \
  --N 20000 \
  --mu 10 \
  --scale 1.5 \
  --sigma 0.954 \
  --plummer-r 10 \
  --n-iterations 20

echo
echo "Preprocess data:"
python preprocess_snap.py \
  --nemo-file snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

echo
echo "Start evolution 100 dynamical times for: M & A"
gyrfalcON snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/IC_preprocessed.nemo \
  snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/out.nemo \
  logstep=300 \
  eps=0.0003684031498640387 \
  kmax=16 \
  tstop=0.06855891525557327 \
  step=6.855891525557327e-06 \
  Grav=4.30091727067736e-06
