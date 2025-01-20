#!/bin/bash

NBODY=1024
TCRIT=1.0

mkplummer p.snap $NBODY seed=123

# nbody6 single processor
time runbody6 p.snap run2 tcrit=$TCRIT deltat=0.1 dtadj=0.05 nbody6=1 exe=nbody6
snapprint run2/OUT3.snap key,x,y,z,vx,vy,vz times=1 | head -4

# nbody6 SSE multiprocessor
time runbody6 p.snap run3 tcrit=$TCRIT deltat=0.1 dtadj=0.05 nbody6=1 exe=nbody7b.sse
snapprint run3/OUT3.snap key,x,y,z,vx,vy,vz times=1 | head -4
