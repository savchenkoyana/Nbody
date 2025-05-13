# About

The goal of this experiment is to create a PBH globular cluster and run its evolution.

# How to reproduce

## Prepare environment and binaries

- Activate the Agama environment:

  ```bash
  conda activate agama
  ```

- Start Nemo (from `nemo` repository root):

  ```bash
  source start_nemo.sh
  ```

- Go to the experiment root directory:

  ```bash
  cd /path/to/Nbody/03_MW_PBH_cluster/
  ```

- Prepare binaries (only once):

  ```bash
  ln -s ~/work/Nbody/Nbody6ppGPU/build/nbody6++.avx nbody6pp
  ln -s ~/work/Nbody/Nbody6PPGPU-beijing/build/nbody6++.avx nbody6pp-beijing
  ```

  Note that the name of binaries may differ if you used other options to build them. We will use `nbody6pp-beijing` binary for evolution and `nbody6pp` binary simply to convert data to the right format.

## Create IC

TODO

## Run evolution

Let's suppose that you run evolution from `03_MW_PBH_cluster/DIRNAME` and there is `IC.nemo` in this directory.

- Prepare the input:

  To convert data to units with `G=1` (pc, km/s and $\\sim 232.5337 \\times M\_{☉}$), run:

  ```bash
  snapscale in=IC.nemo \
    out=IC_g1.nemo \
    mscale=4.300451321727918e-03
  ```

  > For more details about units see section [Units](#Units).

  Then transform data into Nbody6pp-format:

  ```bash
  runbody6 in=IC_g1.nemo out=outdir tcrit=0 nbody6=0 exe=nbody6pp
  cp outdir/dat.10 .
  ```

  Then change `Rbar`, `Zmbar` and `Q` fields in your Fortran namelist input file according to this output (run from `02_Reproduce_JGB`):

  ```bash
  python scale.py --length 0.001 --mass 1 --velocity 1 --nemo-file `DIRNAME`/IC.nemo
  ```

  > Use absolute value of `Q`

  Also you may need to alter time in input file (`TCRIT`)

- Run evolution

  ```bash
  cd `OUTDIR`
  /path/to/nbody6pp-beijing< `input_name` 1>exp.out 2>exp.err
  ```

  You may track intermediate results by running (from `02_Reproduce_JGB`):

  ```bash
  bash sh_scripts/grep_on_update.sh ../03_MW_PBH_cluster/`OUTDIR`/exp.out
  ```

  or

  ```bash
  tail -f exp.out
  ```

- Postprocess your data to plot profiles, spectras, etc.

  Snapshot data are stored in `conf.3_*` in Nbody6++GPU-version. To transform it into NEMO snapshot, use:

  ```bash
  cat `ls -tr conf.3_*` > OUT3; u3tos OUT3 out.nemo mode=6 nbody=<N> ; rm OUT3
  ```

  where `<N>` is the number of particles in your simulation.

  Then to transform to astrophysical units:

  ```bash
  snapscale in=out.nemo \
    out=out_scaled.nemo \
    mscale=<mscale> \
    rscale=<rscale> \
    vscale=<vscale>
  ```

  These coefficients are automatically computed in Nbody6++GPU and are listed in log file (see `R*`, `V*`, `T*`, and `M*`)

# Explore results

(Todo : move from `02_Reproduce_JGB`)

## Visualize cluster evolution

- To visualize cluster evolution, run:

  ```bash
  snapplot <DIRNAME>/out.nemo
  ```

  Use these options for customization:

  ```bash
  snapplot <DIRNAME>/out.nemo xrange=<xmin>:<xmax> yrange=<ymin>:<ymax> times=<tmin>:<tmax>
  ```

- There is also a possibility to visulaize the evolution using [glnemo2](https://projets.lam.fr/projects/glnemo2/wiki/download).

- Another option is to use custom visualization script from this repository:

  ```bash
  python animate.py --nemo-file <DIRNAME>/out.nemo
  ```

  Use `--xlim` and `--ylim` to set your own limits.

## Plot density profile $$\\rho(r)$$

TODO

## Plot logged data

To plot data stored in log file run something like this:

- In Nbody units:

  ```bash
  python plot_nbody6_logdata.py --log-file `OUTDIR`/exp.out --values RLAGR
  ```

- In astro units:

  ```bash
  python plot_nbody6_logdata.py --log-file `OUTDIR`/exp.out --values RLAGR --astro-units
  ```

To check other options run:

  ```bash
  python plot_nbody6_logdata.py --help
  ```

# Units

We use non-usual units in our experiments:

- We use astrophysical units for creating a cluster model because of convenience:
  - pc (length)
  - km/s (velocity)
  - $M\_{☉}$ (mass)
- We use units with `G=1` to feed data into N-body code:
  - pc (lenght)
  - km/s (velocity)
  - $\\sim 232.5337 \\times M\_{☉}$ (mass)
- The output should be manually converted into astrophysical units

# Checklist

- [ ] First simple models for LMC, SMC, M31
- [ ] Check different cluster size
- [ ] Different IMF
- [ ] Check spin dependency
