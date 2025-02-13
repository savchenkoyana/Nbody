# About

This document shows how to compare our results with other direct N-body methods as well as GyrFalcON.

# How to reproduce

To reproduce the experiment, follow these steps:

- Activate the Agama environment:

  ```shell
  conda activate agama
  ```

- Start Nemo (from `nemo` repository root):

  ```shell
  source start_nemo.sh
  ```

- Go to the experiment root directory:

  ```shell
  cd /path/to/Nbody/02_Reproduce_JGB/
  ```

- At the moment I compare gyrfalcON with Nbody0 (the simplest Nbody method). GyrFalcON is not designed to treat dense clusters, but it is possible to get more or less correct results by setting gyrFalcON's `theta` to a very low value. The best results I got for `N=10000` and $\\sigma=1.5$:

  ```shell
  gyrfalcON snap_mu0.0_s1.0_sigma1.5_r10.0_N10000/IC_preprocessed_nbody.nemo \
    snap_mu0.0_s1.0_sigma1.5_r10.0_N10000/out_g1_kmax15_Nlev8_theta01_fac001.nemo \
    kmax=15 \
    Nlev=8 \
    logstep=3000 \
    eps=0.0003684031498640387 \
    tstop=14 \
    step=0.01 \
    theta=0.1 \
    fac=0.01
  ```

- This scripts demonstrates evolution on $\\sigma=1.5$ with different N-body methods:

  ```shell
  bash sh_scripts/run_simN1000.sh
  ```

# Results interpretation

You can compare different integrators visually (by running `animate.py`) or plot all snapshot statistics: density profile, mass spectrum or lagrange radius.

To plot lagrange radii for different methods together, run this command:

```shell
python plot_lagrange_radius.py \
  --remove-outliers \
  --nemo-files /path/to/dir1/out_postprocessed.nemo ... /path/to/dirn/out_postprocessed.nemo \
  --mu <MU> \
  --sigma <SIGMA> \
  --scale <SCALE> \
  --nbody-nemo-files /path/to/dirn/out_nbody_postprocessed.nemo \
```

> Do not forget to use post-processed data (without SMBH at the center) with the command above

It can be useful to plot energy, virial ratio, angular momentum as a function of time for both simulations:

```shell
python stat.py --nemo-files <DIRNAME>/<OUT_NAME>.nemo --eps <eps> --virial --momentum --binaries
```

> Use the same `<eps>` as during the simulation. Do not use postprocessed snapshot with removed central mass.

# Tips

1. To resume gyrFalcON simulation, run:
   ```shell
   gyrfalcON in=<NAME>.nemo ... resume=t  # not tested properly yet
   ```
   `<NAME>.nemo` is the name of output file of the interrupted run, `out=` is ignored, and `resume=t` indicates that we want to resume simulation. The rest of the command for gyrFalcON (marked here as `...`) should be exactly the same.
1. If Aarseth's NBODY code does not save a snapshot, use NEMO's `u3tos`
1. If you forgot how you created your snapshot, just run:
   ```shell
   hisf <NAME>.nemo
   ```
1. A list of hacks on how to check N-body simulation results is given [here](https://arxiv.org/pdf/1105.1082).

# About direct methods

The detailed description of different direct methods was [given](https://www.jstor.org/stable/10.1086/316455) by Aarseth.
