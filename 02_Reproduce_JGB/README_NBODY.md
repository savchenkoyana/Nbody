# About

This document shows how to run simulation with older direct N-body methods as well as GyrFalcON.

# How to reproduce

To reproduce the experiment, follow these steps:

- Activate the Agama environment:

  ```bash
  conda activate agama
  ```

- Start Nemo (from `nemo` repository root):

  ```bash
  source start_nemo.sh
  ```

  Note that you may neeed to rebuild some binaries if you want to run simulation with large number of particles. For that, use custom NEMO version from https://github.com/savchenkoyana/nemo.git (branch `nbodyx`):

  ```bash
  cd $NEMO
  git remote add custom https://github.com/savchenkoyana/nemo.git
  git checkout nbodyx
  cd $NEMO/src/nbody/evolve/aarseth/nbody0
  make nmax
  cd $NEMO/src/nbody/evolve/aarseth/nbody1/source
  make nmax
  cd $NEMO/src/nbody/evolve/aarseth/nbody2/source
  make nmax
  cd $NEMO/src/nbody/reduc/Makefile
  make snapbinary
  cp snapbinary $NEMOLIB/
  cd $NEMO
  make rebuild
  ```

  If you run simulation with ~1000 particles you don't need to do anything other than default installation.

- Go to the experiment root directory:

  ```bash
  cd /path/to/Nbody/02_Reproduce_JGB/
  ```

- To make fast checks that everything works fine, run:

  ```bash
  bash sh_scripts/compare_methods_fast.sh
  ```

- To start full simulation with different N-body methods, run:

  ```bash
  bash sh_scripts/run_othermethods.sh <N> <TASK> <ETA>
  ```

  At first I recommend to choose `N=1000` (you can set a higher `N` later). Use options `1000 -1` to create coordinates and then `1000 0`, `1000 1`, `1000 2`, etc. to run all N-body methods.

# Results interpretation

You can compare different integrators visually (by running `animate.py`) or plot all snapshot statistics: density profile, mass spectrum or lagrange radius.

> There is no way to incorporate a potential of SMBH for **Nbody0, Nbody1, and Nbody2** (although it is possible for **GyrFalcON**, I don't do it for the sake of consistency). So to compare Nbody6 with these methods, I manually insert a body representing SMBH, shift the cluster position and velocity and then run the simulation. After that we need to post-process data (get rid of SMBH and remove shift in distance/velocity of the cluster) to get the result in the same form as Nbody6. Do not forget to use post-processed data (without SMBH at the center) for analysis when needed (see `sh_scripts/run_nbody0.sh` for details)

To plot lagrange radii for different methods together, run this command:

```bash
python plot_lagrange_radius.py \
  --remove-outliers \
  --nemo-files /path/to/dir1/out_postprocessed.nemo ... /path/to/dirn/out_postprocessed.nemo \
  --mu <MU> \
  --sigma <SIGMA> \
  --scale <SCALE>
```

> Use `plot_lagrange_radius.py`, `plot_mass_spectrum.py` and `plot_density_profile.py` with post-processed data (without central BH).

Plot energy, virial ratio, angular momentum as a function of time:

```bash
python stat.py --nemo-files <DIRNAME>/<OUT_NAME>.nemo --eps <eps> --virial --momentum --binaries
```

> Use the same `<eps>` as during the simulation. Do not use postprocessed snapshot with removed central mass.

# Tips

1. To resume gyrFalcON simulation, run:
   ```bash
   gyrfalcON in=<NAME>.nemo ... resume=t  # not tested properly yet
   ```
   `<NAME>.nemo` is the name of output file of the interrupted run, `out=` is ignored, and `resume=t` indicates that we want to resume simulation. The rest of the command for gyrFalcON (marked here as `...`) should be exactly the same.
1. If Aarseth's NBODY code does not save a snapshot, use NEMO's `u3tos` with key `mode=X`, where `X` is your algorithm version (`mode=1` for Nbody1, `mode=4` for Nbody4, etc.)
1. If you forgot how you created your snapshot, just run:
   ```bash
   hisf <NAME>.nemo
   ```
1. A list of hacks on how to check N-body simulation results is given [here](https://arxiv.org/pdf/1105.1082).
1. There is another way to start an Aarseth simulation, e.g. use [`nbody1`](https://teuben.github.io/nemo/man_html/nbody1.1.html) instead of its NEMO wrapper [`runbody1`](https://teuben.github.io/nemo/man_html/runbody1.1.html). For more details see `$NEMO/src/nbody/evolve/aarseth/tools/`
1. Some useful info about run options can be found in file `define.f` (see either `$NEMO/src/nbody/evolve/aarseth/nbody*` or nbody6 source code from `ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz`, depending on your NbodyX version)
1. Nbody codes save data in N-body units by default. To transform your data into astrophysical units (pc, km/s, $M\_{☉}$), use coefficients from simulation log. You can also perfrom scaling to N-body units yourself and compute coefficients using [scale.py](scale.py)

# About direct methods

The detailed description of different direct methods was [given](https://www.jstor.org/stable/10.1086/316455) by Aarseth.

I use Nbody6 from NEMO (taken from Aarseth's site `ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz`) and [Nbody6PPGPU-beiging](https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing) which is the GPU version supported by developers at the moment.
