#!/bin/bash

# Set these 2 parameters
NBODY=10000
WORKING_DIR="nbody4_vs_gyrfalcon"


# Parameters for gyrFalcON are chosen according to https://td.lpi.ru/~eugvas/nbody/tutor.pdf
if [[ $NBODY == 1000 ]]; then
   EPS=0.1
elif [[ $NBODY == 10000 ]]; then
   EPS=0.045
else
   echo "Invalid NBODY=$NBODY! Choose one of: 1000, 10000"
   exit 1
fi


IC="$WORKING_DIR/IC.nemo"
OUT_NBODY="$WORKING_DIR/out_nbody"
OUT_FALC="$WORKING_DIR/out_falc.nemo"


echo "===================================="
echo "Statistics for $IC"
echo "===================================="
snapvratio "$IC" wmode=exact eps=$EPS newton=t 2>&1 | tee "$WORKING_DIR/vir_IC"
echo

echo "===================================="
echo "Statistics for $OUT_FALC"
echo "===================================="
snapvratio "$OUT_FALC" wmode=exact eps=$EPS newton=t | tee "$WORKING_DIR/vir_FALC"
echo

echo "===================================="
echo "Statistics for $OUT_NBODY"
echo "===================================="
snapvratio "$OUT_NBODY/OUT3.snap" wmode=exact eps=$EPS newton=t | tee "$WORKING_DIR/vir_NBODY"
