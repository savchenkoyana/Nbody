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

  Note that you neeed custom NEMO version from https://github.com/savchenkoyana/nemo.git (branch nbodyx). To check your current branch, run:

  ```shell
  git status
  ```

  If your version differs, use installation instruction from \[README.md\]

- Go to the experiment root directory:

  ```shell
  cd /path/to/Nbody/02_Reproduce_JGB/
  ```

- To make fast checks that everything works fine, run:

  ```shell
  bash sh_scripts/compare_methods_fast.sh
  ```

- To start full simulation with different N-body methods, run:

  ```shell
  bash sh_scripts/compare_methods_slow.sh <N> <TASK>
  ```

  At first I recommend to choose `N=1000` (you can set a higher `N` later). Use options `1000 0` to create coordinates and then `1000 1`, `1000 2`, `1000 3`, etc. to run all N-body methods.

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
