#!/bin/bash

echo "Usage: bash sh_scripts/run_exp.sh <N> <EXP>"
echo "Choose <N> from: 1000, 2000, 5000, 10000, 20000"
echo "<EXP> should be:"
echo "1 --- MU=10, SCALE=1.5, SIGMA=0.954;"
echo "2 --- MU=0 , SCALE=1  , SIGMA=0.5  ;"
echo "3 --- MU=0 , SCALE=1  , SIGMA=1.0  ;"
echo "4 --- MU=0 , SCALE=1  , SIGMA=1.5  ;"
echo

if [ $# -ne 2 ]; then
    echo "Wrong number of arguments!"
    exit 1
fi

N=$1
EXP=$2

if [[ $N == 1000 ]]; then
   EPS=1.0
elif [[ $N == 2000 ]]; then
   EPS=0.79
elif [[ $N == 5000 ]]; then
   EPS=0.58
elif [[ $N == 10000 ]]; then
   EPS=0.46
elif [[ $N == 20000 ]]; then
   EPS=0.368
else
   echo "Invalid N=$N! Choose one of: 1000, 2000, 5000, 10000, 20000"
   exit 1
fi

if [[ $EXP == 1 ]]; then
    MU=10.0
    SCALE=1.5
    SIGMA=0.954
elif [[ $EXP == 2 ]]; then
    MU=0.0
    SCALE=1.0
    SIGMA=0.5
elif [[ $EXP == 3 ]]; then
    MU=0.0
    SCALE=1.0
    SIGMA=1.0
elif [[ $EXP == 4 ]]; then
    MU=0.0
    SCALE=1.0
    SIGMA=1.5
else
   echo "Invalid EXP=$EXP! Should be 1, 2, 3 or 4"
   exit 1
fi


ETA=0.01
ROOT_DIR="snap_mu${MU}_s${SCALE}_sigma${SIGMA}_r10.0_N${N}"

echo "Generate coordinates for experiment: MU=${MU} SCALE=${SCALE} SIGMA=${SIGMA}"
python create_ic.py \
  --N $N \
  --mu $MU \
  --scale $SCALE \
  --sigma $SIGMA \
  --plummer-r 10 \
  --n-iterations 20

echo
echo "Preprocess data:"
python preprocess_snap.py \
  --nemo-file $ROOT_DIR/IC.nemo \
  --r-shift 34 0 0 \
  --v-shift 0 -74.35014 0 \
  --plummer-r 10 \
  --add-point-source \
  --source-mass 4.37e10

echo
echo "Preprocess data..."
snapscale in=$ROOT_DIR/IC_preprocessed.nemo \
  out=$ROOT_DIR/IC_preprocessed_g1.nemo \
  mscale=4.300451321727918e-03 \
  rscale=1000

echo
echo "Start evolution with NBODY0 for 13.7 Gyr for: M & A"
nice -n 20 nbody0 $ROOT_DIR/IC_preprocessed_g1.nemo \
  $ROOT_DIR/out_nbody.nemo \
  tcrit=14000 \
  deltat=100 \
  eta=$ETA \
  eps=$EPS

echo
echo "Postprocess data:"
python postprocess_snap.py \
  --snap-file $ROOT_DIR/out_nbody.nemo \
  --remove-point-source \
  --source-mass 4.37e10 \
  --length 0.001 \
  --mass 232.5337331 \
  --velocity 1.0

echo
echo "Calculating timestamps..."
python stat.py \
  --nemo-files $ROOT_DIR/out_nbody.nemo \
  --n-timestamps 100 > $ROOT_DIR/timestamps_nbody.txt

python stat.py \
  --nemo-files $ROOT_DIR/out_nbody.nemo \
  --n-timestamps 10 >> $ROOT_DIR/timestamps_nbody.txt
