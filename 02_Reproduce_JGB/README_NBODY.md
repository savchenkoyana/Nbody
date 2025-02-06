# About

This document shows how to reproduce the experiment with direct N-body methods. Many researchers use Nbody6++GPU in order to perform evolution of clusters. We need to compare our method (fast gytFalcON with complexity $O(N)$) with precise but slow Nbodyx methods (Nbody0, Nbody4, Nbody6, etc.) with complexity $O(N^2)$ to make sure that our method suits good for this task.

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

- Switch to custom NEMO version:

  ```shell
  cd $NEMO
  git remote add custom https://github.com/savchenkoyana/nemo.git
  git checkout nbodyx
  cd $NEMO/src/nbody/evolve/aarseth/nbody0
  make nmax
  cd $NEMO/src/nbody/evolve/aarseth/nbody1/source
  make nmax
  cd $NEMO/src/nbody/reduc/Makefile
  make snapbinary
  cp snapbinary $NEMOLIB/
  cd $NEMO
  make rebuild
  ```

  If you want to go back to the default NEMO version, run:

  ```shell
  cd $NEMO
  git checkout master
  make rebuild
  ```

- Go to the experiment root directory:

  ```shell
  cd /path/to/Nbody/02_Reproduce_JGB/
  ```

- At the moment I compare gyrfalcON with Nbody0 (the simplest Nbody method). To run both gyrFalcON and Nbody0 methods together, use `1` in a bash script for evolution:

  ```shell
  bash sh_scripts/run_exp_MA.sh 1
  ```

  > The default command `bash sh_scripts/run_exp_MA.sh` is equivalent to `bash sh_scripts/run_exp_MA.sh 0`, the latter argument means whether to run Nbody0 or not.

  > It takes about 4 hours to run a gyrFalcON simulation on our CPU. Running Nbody0 simulation takes about 3 days depending on task you choose. Running M & A experiment with `N = 20000` was not reasonable because it would take us more than two weeks, so we used `N = 10000` for this experiment.

## Compare results

You can compare gyrFalcON and Nbody0 results visually (by running `animate.py`) or plot all statistics: density profile, mass spectrum or lagrange radius.

To plot lagrange radii for gyrFalcON and Nbody0 together, run this command:

```shell
python plot_lagrange_radius.py \
  --remove-outliers \
  --nemo-files /path/to/dir1/out_postprocessed.nemo ... /path/to/dirn/out_postprocessed.nemo \
  --mu <MU> \
  --sigma <SIGMA> \
  --scale <SCALE> \
  --nbody-nemo-files /path/to/dirn/out_nbody_postprocessed.nemo \
```

It can be useful to plot energy, virial ratio, angular momentum as a function of time for both simulations:

```shell
python stat.py --nemo-files <DIRNAME>/<OUT_NAME>.nemo --eps <eps> --virial
```

For this procedure you need snapshots with `G=1`. Use the same `<eps>` as during the simulation. Do not use postprocessed snapshot with removed central mass.

# Units

The main diffrence between Nbody0 and gyrFalcON is that Nbody0 always uses `G=1`. We use another units for evolution: kpc for lenght, km/s for velocity and $M\_{☉}$ for mass. With that in mind, I decided that the easiest choice of units for Nbody0 is: kpc, km/s and $\\sim 232533.7 \\times M\_{☉}$:

- In these units `G=1` by definition
- It is easy to compare results of evolution between Nbody0 and gyrFalcON and reuse the same scripts, as we do not need to change the time, velocity and length scale. We only change the mass scale.

# Tips

1. If you forgot how you created your snapshot, just run:
   ```shell
   hisf <NAME>.nemo
   ```
1. If Aarseth's NBODY code does not save a snapshot, use NEMO's `u3tos`
