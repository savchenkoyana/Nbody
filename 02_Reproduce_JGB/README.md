This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido (shortly: JGB).

The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.

![](../images/log_normal_mass.png)

Mass spectra used in the article.

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

- Go to the experiment root directory:

  ```bash
  cd /path/to/Nbody/02_Reproduce_JGB/
  ```

- Prepare binaries (only once):

  ```bash
  ln -s ~/work/Nbody/Nbody6ppGPU/build/nbody6++.avx nbody6pp
  ln -s ~/work/Nbody/Nbody6PPGPU-beijing/build/nbody6++.avx nbody6pp-beijing
  ```

  Note that the name of binaries may differ if you used other options to build them. We will use `nbody6pp-beijing` binary for evolution and `nbody6pp` binary simply to convert data to the right format.

- Create initial coordinates of cluster:

  ```bash
  python create_ic.py --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS> --N <N>
  ```

  Here `N` is the number of particles in simulation, `MU`, `SIGMA`, and `SCALE` are log-normal distribution parameters of PBH mass spectrum, and `PLUMMER_RADIUS` is a characteristic size of Plummer density distribution (type `python create_ic.py --help` for more details).

  The above command will automatically create (or re-create) a directory with name `snap_mu<MU>_s<SCALE>_sigma<SIGMA>_r<PLUMMER_RADIUS>_N<N>` containing file `IC.nemo` with initial coordinates for evolution.

- Prepare the input:

  To convert data to units with `G=1` (pc, km/s and $\\sim 232.5337 \\times M\_{☉}$), run:

  ```bash
  snapscale in=<OUTDIR>/IC.nemo \
    out=<OUTDIR>/IC_g1.nemo \
    mscale=4.300451321727918e-03
  ```

  > For more details about units see section [Units](#Units).

  Then transform data into Nbody6pp-format:

  ```bash
  runbody6 in=<OUTDIR>/IC_g1.nemo out=<OUTDIR>/outdir tcrit=0 nbody6=0 exe=nbody6pp
  cp <OUTDIR>/outdir/dat.10 <OUTDIR>/
  ```

  Then change `Rbar`, `Zmbar` and `Q` fields in your Fortran namelist input file (<OUTDIR>/input) according to this output:

  ```bash
  python scale.py --length 0.001 --mass 1 --velocity 1 --nemo-file <OUTDIR>/IC.nemo
  ```

  > Use absolute value of `Q`

  Also you may need to alter time in input file (`TCRIT`)

- Run evolution

  ```bash
  cd <OUTDIR>
  /path/to/nbody6pp-beijing< <input_name> 1>exp.out 2>exp.err
  ```

  You may track intermediate results by running (from exp root):

  ```bash
  bash sh_scripts/grep_on_update.sh <OUTDIR>/exp.out
  ```

  or

  ```bash
  tail -f <OUTDIR>/exp.out
  ```

- Postprocess your data to plot profiles, spectras, etc.

  Snapshot data are stored in `conf.3_*` in Nbody6++GPU-version. To transform it into NEMO snapshot, use:

  ```bash
  cat `ls -tr conf.3_*` > OUT3; u3tos OUT3 out.nemo mode=6 nbody=<N> ; rm OUT3
  ```

  where `<N>` is the number of particles in your simulation.

  Then to transform to astrophysical units:

  ```bash
  python snapscale.py --exp <OUTDIR>
  ```

  and finally:

  ```bash
  rm <OUTDIR>/out.nemo  # for saving space
  ```

  The resulting file will be `<OUTDIR>/out_scaled.nemo`

# Explore results

## Visualize cluster evolution

- To visualize cluster evolution, run:

  ```bash
  snapplot <OUTDIR>/out.nemo
  ```

  Use these options for customization:

  ```bash
  snapplot <OUTDIR>/out.nemo xrange=<xmin>:<xmax> yrange=<ymin>:<ymax> times=<tmin>:<tmax>
  ```

- There is also a possibility to visulaize the evolution using [glnemo2](https://projets.lam.fr/projects/glnemo2/wiki/download).

- Another option is to use custom visualization script from this repository:

  ```bash
  python animate.py --nemo-file <OUTDIR>/out.nemo
  ```

  Use `--xlim` and `--ylim` to set your own limits.

## Plot density profile $$\\rho(r)$$

Run:

```bash
python plot_density_profile.py --N 5000 --mu 10 --scale 1.5 --sigma 0.954 --nemo-file <OUTDIR>/out_scaled.nemo --n-timestamps 5
```

## Plot Lagrange radii

The easiest way to plot lagrange radii is to use data stored in log file:

- In Nbody units:

  ```bash
  python plot_nbody6_logdata.py --log-file <OUTDIR>/exp.out --values RLAGR
  ```

- In astro units:

  ```bash
  python plot_nbody6_logdata.py --log-file <OUTDIR>/exp.out --values RLAGR --astro-units
  ```

Note that you can also use `plot_lagrange_radius.py`. Use `out_scaled.nemo` to plot in astrophysical units.

> Note that if you don't remove escapers, the results may differ! You can remove escapers at post-processing using `remove_escapers.py` and re-run `plot_lagrange_radius.py` with post-processed data

Use `plot_stats.py` to plot $N(t)$ and $M(t)$ (these should be constant if you don't remove escapers)

You can compare your results with plots from the article:

![](../images/lagrange_radii.png)

![](../images/cluster_stat.png)

Note that Lagrange radius at $t=0$ should be approximately 13 pc according to [analytical expression](https://en.wikipedia.org/wiki/Plummer_model) for Plummer with size 10 pc.

## Plot mass spectrum $$f(M)$$

Plot how mass changes with distance from center:

- In Nbody units:

  ```bash
  python plot_nbody6_logdata.py --log-file <OUTDIR>/exp.out --values AVMASS
  ```

- In astro units:

  ```bash
  python plot_nbody6_logdata.py --log-file <OUTDIR>/exp.out --values AVMASS --astro-units
  ```

# Compare with other N-body methods

The comparison with other methods is descriped in details in [README_NBODY.md](README_NBODY.md).

# Explore mergers and GW radiation

Use:

```bash
grep "GR " -A 2 -B 2 nbody6++jgb_exp/N5000_MA/exp.out
```

```bash
grep "NMERGE" nbody6++jgb_exp/N5000_MA/exp.out
```

```bash
grep "NEW MERGER" nbody6++jgb_exp/N5000_MA/exp.out
```

```bash
grep "NBH" -A 1 nbody6++jgb_exp/N5000_MA/exp.out
```

and

```bash
grep "NS/BH BINARY" nbody6++jgb_exp/N5000_MA/exp.out
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
- Nbody6++GPU uses N-body units (and produces output in N-body units), other codes here compute the evolution as is (see `sh_scripts/run_othermethods.sh`)

# Checklist

Here is a list of what we need to fully reproduce the article:

- [x] Comparison with other methods
- [x] Nbody6 (simple run)
- [ ] Gravitational waves + Black hole mergers
- [ ] Natal spins = 0 (random with `KZ(24)=2`)
