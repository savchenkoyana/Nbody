#!/bin/bash

echo "This script is used to run full simulation with variuos N-body methods"
echo "Usage: bash sh_scripts/compare_methods_slow.sh <N> <TASK> <ETA>"
echo
echo "<N> should be one of: 1000, 2000, 5000, 10000"
echo "<TASK> should be:"
echo "-1 --- to create IC;"
echo "0 --- to run nbody0;"
echo "1 --- to run runbody1;"
echo "2 --- to run runbody2;"
echo "4 --- to run runbody4 (SMBH as external potential);"
echo "6 --- to run runbody6 (SMBH as external potential);"
echo "Choose <ETA> carefully (default value is 0.02)"
echo

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Wrong number of arguments!"
    exit 1
fi

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
IC_G1="${DIR}/IC_g1.nemo"
IC_PREPROCESSED_G1="${DIR}/IC_preprocessed_g1.nemo"

if [[ $TASK -eq -1 ]]; then
  echo "Creating IC"

  python create_ic.py \
    --N $N \
    --mu 0 \
    --scale 1 \
    --sigma 1.5 \
    --plummer-r 10 \
    --n-iterations 20

  # This part is for Nbody0, Nbody1 and Nbody2 ONLY!
  python preprocess_snap.py \
    --nemo-file $DIR/IC.nemo \
    --r-shift 34 0 0 \
    --v-shift 0 -74.35014 0 \
    --plummer-r 10 \
    --add-point-source \
    --source-mass 4.37e10

  snapscale in=$DIR/IC_preprocessed.nemo \
    out=$IC_PREPROCESSED_G1 \
    mscale=4.300451321727918e-03 \
    rscale=1000

  # This part is for Nbody4 and Nbody6
  snapscale in=$DIR/IC.nemo \
    out=$IC_G1 \
    mscale=4.300451321727918e-03

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
    --snap-file $OUTFILE \
    --remove-point-source \
    --length 0.001 \
    --mass 232.5337331 \
    --velocity 1.0

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
    --snap-file "${OUTDIR}/OUT3.snap" \
    --remove-point-source \
    --length 0.001 \
    --mass 232.5337331 \
    --velocity 1.0

elif [[ $TASK -eq 2 ]]; then
  echo "Running runbody2"

  OUTDIR="${DIR}/runbody2_ETA${ETA}_ETAR${ETAR}_EPS${EPS}"

  # Nbody2
  time nice -n 20 runbody2 \
    in=$IC_PREPROCESSED_G1 \
    tcrit=14000 \
    deltat=100 \
    nbody=$NPART \
    eps=$EPS \
    etai=$ETA \
    etar=$ETAR \
    KZ6=0 \
    tcomp=4000 \
    outdir=$OUTDIR

  u3tos "${OUTDIR}/OUT3" \
    "${OUTDIR}/OUT3.snap" \
    mode=2

  python postprocess_snap.py \
    --snap-file "${OUTDIR}/OUT3.snap" \
    --remove-point-source \
    --length 0.001 \
    --mass 232.5337331 \
    --velocity 1.0

elif [[ $TASK -eq 4 ]]; then
  echo "Running runbody4 with SMBH as external potential"

  if [[ $N -ne 1000 ]]; then
    echo "Not implemented for N=$N! Please use 1000 or modify code"
    exit 1
  fi

  OUTDIR="${DIR}/runbody4_ETA${ETA}"
  mkdir $OUTDIR

  cp sh_scripts/nbodyx_inputs/nbody4.in $OUTDIR
  cd $OUTDIR

#  # create fort.10
#  runbody6 "../IC_g1.nemo" "outdir" tcrit=0 nbody=$N nbody6=1 exe=nbody6 kz=1,2,1 KZ22=3
#  cp "outdir/fort.10" .  # fort.10 in arbitrary units with G=1

  # create fort.10
  runbody4 "../IC_g1.nemo" "outdir" tcrit=0 nbody=$N KZ22=2 body1=1.0 bodyn=1.0
  cp "outdir/fort.10" .  # fort.10 in arbitrary units with G=1

  time nice -n 20 nbody4 < nbody4.in 2>&1 | tee -a log.out

  u3tos "OUT3" "OUT3.snap" mode=4
  cd ..

elif [[ $TASK -eq 6 ]]; then
  echo "Running runbody6 with SMBH as external potential"

  if [[ $N -ne 5000 ]]; then
    echo "Not implemented for N=$N! Please use 5000 or modify code"
    exit 1
  fi

  OUTDIR="${DIR}/runbody6_ETA${ETA}_ETAR${ETAR}"
  mkdir $OUTDIR

  cp sh_scripts/nbodyx_inputs/nbody6.in $OUTDIR
  cd $OUTDIR

  # create fort.10
  runbody6 "../IC_g1.nemo" "outdir" tcrit=0 nbody=$N nbody6=1 exe=nbody6
  cp "outdir/fort.10" .  # fort.10 in arbitrary units with G=1

  time nice -n 20 nbody6 < nbody6.in 2>&1 | tee -a log.out

  u3tos "OUT3" "OUT3.snap" mode=6
  cd ..

fi
