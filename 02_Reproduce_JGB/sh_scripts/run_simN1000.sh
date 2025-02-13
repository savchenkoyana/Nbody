#!/bin/bash

# Eps = 0.001

python create_ic.py --N 1000 --mu 0 --scale 1 --sigma 1.5 --plummer-r 10 --n-iterations 20

python preprocess_snap.py \
  --nemo-file snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

snapscale in=snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC_preprocessed.nemo \
  out=snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC_preprocessed_nbody.nemo \
  mscale=4.300451321727918e-06

# Nbody1
nice -n 20 runbody1 \
  in=snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC_preprocessed_nbody.nemo \
  deltat=0.1 \
  tcrit=14 \
  nbody=1001 \
  eps=0.001 \
  eta=0.001 \
  outdir=snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/runbody1_eta1e-3

# Nbody0
nice -n 20 nbody0 \
  snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC_preprocessed_nbody.nemo \
  snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/out_nbody0_eta1e-3.nemo \
  tcrit=14 \
  deltat=0.01 \
  eps=0.001 \
  eta=0.001

# GyrFalcON
gyrfalcON snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/IC_preprocessed_nbody.nemo \
  snap_mu0.0_s1.0_sigma1.5_r10.0_N1000/out_g1_kmax15_Nlev8_theta01_fac001.nemo \
  kmax=15 \
  Nlev=8 \
  logstep=3000 \
  eps=0.001 \
  tstop=14 \
  step=0.01 \
  theta=0.1 \
  fac=0.01
