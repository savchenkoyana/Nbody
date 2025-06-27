#!/bin/bash

echo "This script is used to run full simulation with variuos N-body methods"
echo "Usage: bash sh_scripts/compare_methods_slow.sh <N> <TASK> <ETA>"
echo
echo "<TASK> should be:"
echo "-1 --- to create IC;"
echo "0 --- to run nbody0;"
echo "1 --- to run runbody1;"
echo "2 --- to run gyrfalcon;"
echo "Choose <ETA> carefully (default value is 0.02)"
echo

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Wrong number of arguments!"
    exit 1
fi

echo "Careful! This script is not completed at the moment and may have mistakes!"

N=$1
TASK=$2
ETA=${3:-0.02}
ETAR=$(echo "2 * $ETA" | bc -l)

EPS=0.01  # default

# EPS computed as a_plummer / N^(1/3), see https://td.lpi.ru/~eugvas/nbody/tutor.pdf
# if [[ $N == 1000 ]]; then
#   EPS=1
# elif [[ $N == 2000 ]]; then
#   EPS=0.79
# elif [[ $N == 5000 ]]; then
#   EPS=0.58
# elif [[ $N == 10000 ]]; then
#   EPS=0.46
# else
#    echo "Invalid N=$N! Choose one of: 1000, 2000, 5000, 10000"
#    exit 1
# fi


NPART=$N+1
DIR="snap_mu0.0_s1.0_sigma1.5_r10.0_N${N}"
IC_PREPROCESSED_G1="${DIR}/IC_preprocessed_g1.nemo"

if [[ $TASK -eq -1 ]]; then
  echo "Creating IC"

  # pc, Msun, km/s
  python create_ic.py \
    --N $N \
    --mu 0 \
    --scale 1 \
    --sigma 1.5 \
    --plummer-r 10 \
    --n-iterations 20

  # Add point mass to snapshot
  # This snapshot is for gyrfalcon
  # Working units are: kpc, Msun, km/s (G=4.30091727067736e-06)
  python preprocess_snap.py \
    --nemo-file $DIR/IC.nemo \
    --r-shift 34 0 0 \
    --v-shift 0 -74.35014 0 \
    --plummer-r 10 \
    --add-point-source \
    --source-mass 4.37e10

  # Another version of snapshot for nbody0 and nbody1
  # Working units are: pc, ~232 Msun, km/s (G=1.0)
  snapscale in=$DIR/IC_preprocessed.nemo \
    out=$IC_PREPROCESSED_G1 \
    mscale=4.300451321727918e-03 \
    rscale=1000

elif [[ $TASK -eq 0 ]]; then
  echo "Running nbody0"

  OUTFILE="${DIR}/out_nbody0_ETA${ETA}_EPS${EPS}.nemo"

  # Nbody0
  time nice -n 20 nbody0 \
    $IC_PREPROCESSED_G1 \
    $OUTFILE \
    tcrit=14000 \
    deltat=100 \
    eps=$EPS \
    eta=$ETA

  python postprocess_snap.py \
    --exp $OUTFILE \
    --version nbody0

elif [[ $TASK -eq 1 ]]; then
  echo "Running runbody1"

  OUTDIR="${DIR}/runbody1_ETA${ETA}_EPS${EPS}"

  # Nbody1
  time nice -n 20 runbody1 \
    in=$IC_PREPROCESSED_G1 \
    tcrit=14000 \
    deltat=100 \
    nbody=$NPART \
    eps=$EPS \
    eta=$ETA \
    KZ6=0 \
    tcomp=4000 \
    outdir=$OUTDIR

  python postprocess_snap.py \
    --exp "${OUTDIR}/OUT3.snap" \
    --version nbody1

elif [[ $TASK -eq 2 ]]; then
  echo "Running gyrfalcon"

  OUTFILE="${DIR}/out_gf.nemo"

  # Hardcoded, best parameters for N=5000 according to eugvas
  # Feel free to modify
  gyrfalcON $DIR/IC_preprocessed.nemo \
    $OUTFILE \
    logstep=3000 \
    eps=0.0005848035476425733 \
    kmax=15 \
    tstop=14.0 \
    step=0.001 \
    Grav=4.30091727067736e-06 \
    theta=0.1

  python postprocess_snap.py \
    --exp $OUTFILE \
    --version gyrfalcon

  # For checking energy conservation by stat.py
  # We use the same units with G=1 as with nbody0, nbody1
  # They are convenient because pc / (km/s) ~ 1 Myr
  # Note that we use original file (without postprocessing) with central BH
  snapscale in=$OUTFILE \
    out="${DIR}/out_gf_g1.nemo" \
    rscale=1e3 \
    mscale=0.004300451322346228

  python stat.py \
    --virial \
    --nemo-files "${DIR}/out_gf_g1.nemo" \
    --eps 0.0005848035476425733e3  # eps in pc
fi
