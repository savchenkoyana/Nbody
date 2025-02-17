#!/bin/bash

echo "Usage: bash sh_scripts/run_exp_MA.sh"

echo "Generate coordinates for experiment: M & A"
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
echo "Preprocess data..."
snapscale in=snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/IC_preprocessed.nemo \
  out=snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/IC_preprocessed_nbody.nemo \
  mscale=4.300451321727918e-06

echo
echo "Start evolution with NBODY0 for 13.7 Gyr for: M & A"
nice -n 20 nbody0 snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/IC_preprocessed_nbody.nemo \
  snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/out_nbody.nemo \
  tcrit=14 \
  deltat=0.01 \
  eps=0.0003684031498640387

echo
echo "Postprocess data:"
python postprocess_snap.py \
  --snap-file snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/out_nbody.nemo \
  --nbody \
  --remove-point-source \
  --source-mass 4.37e10

echo
echo "Calculating timestamps..."
python stat.py \
  --nemo-files snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/out_nbody.nemo \
  --n-timestamps 100 > snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/timestamps_nbody.txt

python stat.py \
  --nemo-files snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/out_nbody.nemo \
  --n-timestamps 10 >> snap_mu10.0_s1.5_sigma0.954_r10.0_N20000/timestamps_nbody.txt
