#!/bin/bash

# Set these 2 parameters
NBODY=10000
WORKING_DIR="nbody4_vs_gyrfalcon"


# Parameters for gyrFalcON are chosen according to https://td.lpi.ru/~eugvas/nbody/tutor.pdf
if [[ $NBODY == 1000 ]]; then
   EPS=0.1
   KMAX=6
elif [[ $NBODY == 10000 ]]; then
   EPS=0.045
   KMAX=8
else
   echo "Invalid NBODY=$NBODY! Choose one of: 1000, 10000"
   exit 1
fi


IC="$WORKING_DIR/IC.nemo"
OUT_NBODY="$WORKING_DIR/out_nbody"
OUT_FALC="$WORKING_DIR/out_falc.nemo"

if [ -d "$WORKING_DIR" ]; then
    rm -Rf $WORKING_DIR;
fi

mkdir "$WORKING_DIR"


mkplummer out=$IC nbody=$NBODY scale=1

# Run gyrFalcON for 20 crossing times (`t_cr ~ a_plummer / v_esc ~ 1.0 / sqrt(2) = 0.707`).
gyrfalcON $IC $OUT_FALC eps=$EPS kmax=$KMAX step=0.25 tstop=15 logstep=100

# Run Runbody4 for `tcrit` = 20 crossing times. Set `ncrit` and `tcomp` to arbitrary large values as they are used for script termination.
runbody4 $IC $OUT_NBODY nbody=$NBODY tcrit=20 deltat=0.25 nfix=1 dtadj=0.25 ncrit=500 tcomp=600
