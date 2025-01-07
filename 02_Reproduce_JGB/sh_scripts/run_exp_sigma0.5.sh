#!/bin/bash

echo "Generate coordinates for experiment: sigma=0.5"
python create_ic.py \
  --N 20000 \
  --mu 0 \
  --scale 1 \
  --sigma 0.5 \
  --plummer-r 10 \
  --n-iterations 20

echo
echo "Preprocess data:"
python preprocess_snap.py \
  --nemo-file snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

echo
echo "Start evolution for 13.7 Gyr for: sigma=0.5"
nice -n 20 gyrfalcON snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/IC_preprocessed.nemo \
  snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/out.nemo \
  logstep=3000 \
  eps=0.0003684031498640387 \
  kmax=15 \
  tstop=14 \
  step=0.01 \
  Grav=4.30091727067736e-06

echo
echo "Postprocess data:"
python postprocess_snap.py \
  --nemo-file snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/out.nemo \
  --remove-point-source \
  --source-mass 4.37e10

echo
echo "Calculating timestamps..."
python stat.py \
  --nemo-file snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/out.nemo \
  --n-timestamps 100 > snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/timestamps.txt

python stat.py \
  --nemo-file snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/out.nemo \
  --n-timestamps 10 >> snap_mu0.0_s1.0_sigma0.5_r10.0_N20000/timestamps.txt
