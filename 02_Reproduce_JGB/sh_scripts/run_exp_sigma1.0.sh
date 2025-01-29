#!/bin/bash

echo "Usage: bash sh_scripts/run_exp_sigma1.0.sh [USE_NBODY](optional)"
echo "[USE_NBODY] should be either 1 (use nbody0 + gyrFalcON) or 0 (only use gyrFalcON, default)"

if [ $# -gt 1 ]; then
    echo "Too many arguments"
    exit 1
fi

use_nbody=${1:-0}

if [[ $use_nbody -eq 0 ]]; then
  echo "Use gyrFalcON"
elif [[ $use_nbody -eq 1 ]]; then
  echo "Use gyrFalcON + nbody0"
else
  echo "Invalid use_nbody = $use_nbody"
  exit 1
fi

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
echo "Start evolution with gyrFalcON for 13.7 Gyr for: sigma=1.0"
nice -n 20 gyrfalcON snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC_preprocessed.nemo \
  snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out.nemo \
  logstep=3000 \
  eps=0.0003684031498640387 \
  kmax=15 \
  tstop=14 \
  step=0.01 \
  Grav=4.30091727067736e-06

echo
echo "Postprocess data:"
python postprocess_snap.py \
  --snap-file snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out.nemo \
  --remove-point-source \
  --source-mass 4.37e10

echo
echo "Calculating timestamps..."
python stat.py \
  --nemo-files snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out.nemo \
  --n-timestamps 100 > snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/timestamps_gyrfalcon.txt

python stat.py \
  --nemo-files snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out.nemo \
  --n-timestamps 10 >> snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/timestamps_gyrfalcon.txt

if [[ $use_nbody -eq 1 ]]; then
  echo
  echo "Preprocess data..."
  snapscale in=snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC_preprocessed.nemo \
    out=snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC_preprocessed_nbody.nemo \
    mscale=4.300451321727918e-06

  echo
  echo "Start evolution with NBODY0 for 13.7 Gyr for: sigma=1.0"
  nice -n 20 nbody0 snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/IC_preprocessed_nbody.nemo \
    snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out_nbody.nemo \
    tcrit=14 \
    deltat=0.01 \
    eps=0.0003684031498640387

  echo
  echo "Postprocess data:"
  python postprocess_snap.py \
    --snap-file snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out_nbody.nemo \
    --nbody \
    --remove-point-source \
    --source-mass 4.37e10

  echo
  echo "Calculating timestamps..."
  python stat.py \
    --nemo-files snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out_nbody.nemo \
    --n-timestamps 100 > snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/timestamps_nbody.txt

  python stat.py \
    --nemo-files snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/out_nbody.nemo \
    --n-timestamps 10 >> snap_mu0.0_s1.0_sigma1.0_r10.0_N20000/timestamps_nbody.txt
fi
