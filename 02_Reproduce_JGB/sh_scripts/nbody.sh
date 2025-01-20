#!/bin/bash

# Set these 2 parameters
NBODY=1000
WORKING_DIR="nbody_vs_gyrfalcon"


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
IC_CLUSTER="$WORKING_DIR/IC_CLUSTER.nemo"
IC_SMBH="$WORKING_DIR/IC_SMBH.nemo"
OUT_NBODY="$WORKING_DIR/out_nbody"
OUT_FALC="$WORKING_DIR/out_falc.nemo"

if [ -d "$WORKING_DIR" ]; then
    rm -Rf $WORKING_DIR;
fi

mkdir "$WORKING_DIR"


mkplummer out=$IC_CLUSTER nbody=$NBODY

echo 0,0,0,0,0,0,100 | tabtos - $IC_SMBH nbody=1 block1=x,y,z,vx,vy,vz,m

snapstack $IC_CLUSTER $IC_SMBH $IC deltar=100,0,0 deltav=0,-2,0

# Run gyrFalcON for 20 crossing times (`t_cr ~ 2 x sqrt(2) = 2.828`).
# Step is 0.25 crossing times
gyrfalcON $IC $OUT_FALC eps=$EPS kmax=$KMAX step=0.707 tstop=56.5685 logstep=100

#nbody0 $IC $OUT_NBODY tcrit=56.5685 deltat=0.707 eps=$EPS
runbody1 $IC $OUT_NBODY tcrit=56.5685 deltat=0.707 eps=$EPS body1=100 bodyn=0.001
