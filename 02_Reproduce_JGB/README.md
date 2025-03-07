# About

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido (shortly: JGB).

The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.

![](../images/log_normal_mass.png)

Mass spectra used in the article.

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
  cd $NEMO/src/nbody/evolve/aarseth/nbody2/source
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

- To reproduce any experiment from the original article, run the corresponding sh-script. For example:

  ```shell
  bash sh_scripts/run_exp_MA.sh
  ```

  You can also choose your own parameters for distributions and run the commands from sh-script one-by-one (see next section).

  > Note that all scripts in this experiment overwrite the existing files.
  > Don't forget to backup your experiments before trying to reproduce them!

  > Running Nbody0 simulation takes about 3 days depending on task you choose. Running M & A experiment with `N = 20000` was not reasonable because it would take us more than two weeks, so it is recommended to use `N = 10000` for this experiment.

The combinations of parameters from the original article and corresponding sh-scripts are listed below:

| Experiment name | $\\mu$, $M\_{☉}$ | s, $M\_{☉}$ | $\\sigma$ | Plummer radius, pc | Number of particles | Command to reproduce evolution     |
| --------------- | ---------------- | ----------- | --------- | ------------------ | ------------------- | ---------------------------------- |
| M & A           | 10               | 1.5         | 0.954     | 10                 | $2 \\times 10^4$    | bash sh_scripts/run_exp.sh 20000 1 |
| $\\sigma$ = 0.5 | 0                | 1           | 0.5       | 10                 | $2 \\times 10^4$    | bash sh_scripts/run_exp.sh 20000 2 |
| $\\sigma$ = 1   | 0                | 1           | 1         | 10                 | $2 \\times 10^4$    | bash sh_scripts/run_exp.sh 20000 3 |
| $\\sigma$ = 1.5 | 0                | 1           | 1.5       | 10                 | $2 \\times 10^4$    | bash sh_scripts/run_exp.sh 20000 4 |

## More detailed overview

This section desctibes how to perform the evolution of PBH cluster in an external potential of SMBH.

- Create initial coordinates of cluster:

  ```shell
  python create_ic.py --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS> --N <N>
  ```

  Here `N` is the number of particles in simulation, `MU`, `SIGMA`, and `SCALE` are log-normal distribution parameters of PBH mass spectrum, and `PLUMMER_RADIUS` is a characteristic size of Plummer density distribution (type `python create_ic.py --help` for more details).

  The above command will automatically create (or re-create) a directory with name `snap_mu<MU>_s<SCALE>_sigma<SIGMA>_r<PLUMMER_RADIUS>_N<N>` containing file `IC.nemo` with initial coordinates for evolution.

- Preprocess data

  JGB writes:

  > Clusters are themselves immersed in a central gravitational potential with orbital radius $R_c$ = 34 kpc and central mass $M = 4.37 × 10^{10} M\_{☉}$ throughout the entire evolution. This is just a point mass approximation which leads to a circular movement of period T = 2.81 Gyr

  The easiest way to create this point-mass potential is to add a new particle representing the central mass to the existing snapshot with PBH cluster data:

  ```shell
  python preprocess_snap.py \
    --nemo-file `DIRNAME`/IC.nemo \
    --r 10 \
    --r-shift 34 0 0 \
    --v-shift 0 -74.35014 0 \
    --add-point-source \
    --source-mass 4.37e10
  ```

  After this step, you will get a new file `<DIRNAME>/IC_preprocessed.nemo` with the old data concatenated with the new data (a steady point of mass $4.37\\times10^{10} M\_\\odot$ at (0, 0, 0)).

  To convert data to units with `G=1` (pc, km/s and $\\sim 232.5337 \\times M\_{☉}$), run:

  ```shell
  snapscale in=`DIRNAME`/IC_preprocessed.nemo \
    out=`DIRNAME`/IC_preprocessed_nbody.nemo \
    mscale=4.300451321727918e-03 \
    rscale=1000
  ```

  For more details see section [Units](#Units).

- Run evolution of this snapshot with SMBH:

  ```shell
  nbody0 `DIRNAME`/IC_preprocessed_nbody.nemo \
    `DIRNAME`/out_nbody0.nemo \
    tcrit=14000 \
    deltat=10 \
    eps=0.3684031498640387
  ```

- It would be useful to postprocess your data to plot profiles, spectras, etc.

  To postprocess snapshot evolved in JGB potential (the original article), run `python postprocess.py`

  The postprocessed file with name `<OUT_NAME>_postprocessed.nemo` will be stored in `<DIRNAME>` folder.

# Explore results

## Visualize cluster evolution

- To visualize cluster evolution, run:

  ```shell
  snapplot <DIRNAME>/out.nemo
  ```

  Use these options for customization:

  ```shell
  snapplot <DIRNAME>/out.nemo xrange=<xmin>:<xmax> yrange=<ymin>:<ymax> times=<tmin>:<tmax>
  ```

- There is also a possibility to visulaize the evolution using [glnemo2](https://projets.lam.fr/projects/glnemo2/wiki/download).

- Another option is to use custom visualization script from this repository:

  ```shell
  python animate.py --nemo-file <DIRNAME>/out_postprocessed.nemo --add-point-source
  ```

## Plot density profile $$\\rho(r)$$

Plot density profile $$\\rho(r)$$ for the resulting snapshot and compare it with initial density:

```shell
python plot_density_profile.py --nemo-file <DIRNAME>/<OUT_NAME>_postprocessed.nemo --times <t1> <t2> ... <tn> --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS>
```

`--times <t1> <t2> ... <tn>` means that all timestamps from snapshot that you want to use to plot the graph should be separated by a space.
E.g., `--times 0.0 1.0 2.0`. Before feeding timestamps, make sure they are present in the snapshot. To get a list of timestamps from a snapshot, run:

```shell
python stat.py --nemo-files <DIRNAME>/<OUT_NAME>_postprocessed.nemo --n-timestamps <N>
```

where `<N>` is the desired number of timestamps.

> If you used sh-scripts, check `txt`-file in directory with your snapshot

## Plot Lagrange radii

To plot Lagrange radius at different timestamps for different experiments, run:

```shell
python plot_lagrange_radius.py --nemo-files <DIRNAME1>/<OUT_NAME>_postprocessed.nemo <DIRNAME2>/<OUT_NAME>_postprocessed.nemo
```

As NEMO's tool for computation of cluster's density center sometimes fail and I haven't fixed it yet, it is better to add `--remove-outliers` at the end of the command:

```shell
python plot_lagrange_radius.py --nemo-files <DIRNAME1>/<OUT_NAME>_postprocessed.nemo <DIRNAME2>/<OUT_NAME>_postprocessed.nemo --remove-outliers
```

You can compare your results with plots from the article:

![](../images/cluster_stat.png)

![](../images/lagrange_radii.png)

Note that Lagrange radius at $t=0$ should be approximately 13 pc according to [analytical expression](https://en.wikipedia.org/wiki/Plummer_model) for Plummer with size 10 pc.

## Plot mass spectrum $$f(M)$$

Compute and plot mass spectrum for a given snapshot along with the original distribution function:

```shell
python plot_mass_spectrum.py --nemo-file <DIRNAME>/<OUT_NAME>_postprocessed.nemo --times <t1> <t2> ... <tn> --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS>
```

The mass distribution for your snapshot (the resulting histograms) and original pdf (the line plot) should look like a log-normal distribution with your parameters at $t=0$. You can compare your results with the picture of log-normal distributions at the beginning of this README document.

To plot the distribution of masses only for particles inside the half-mass radius, run:

```shell
python plot_mass_spectrum.py --nemo-file <DIRNAME>/<OUT_NAME>_postprocessed.nemo --times <t1> <t2> ... <tn> --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS> --lagrange --remove-outliers
```

# Test pipeline

There are several ways to test your pipeline:

1. You may evolve a cluster in its own gravitational field. The final density after the evolution should look like the initial density — this would indicate that your model is truly self-consistent.
   In our case it means that we should not add point mass and shifts when preprocessing.
1. You can check how energy and virial ratio evolve during the simulation:
   ```shell
   python stat.py --nemo-files <DIRNAME>/<OUT_NAME>.nemo --eps <eps> --virial
   ```
   Use the same `<eps>` as during the simulation. Do not use postprocessed snapshot with removed central mass.

# Compare with other N-body methods

The comparison with other methods is descriped in details in [README_NBODY.md](README_NBODY.md).

# Units

We use non-usual units in our experiments:

- We use pc (length), km/s (velocity) and $M\_{☉}$ (mass) units for creating a cluster model because of convenience
- We use units with `G=1` for evolution: pc for lenght, km/s for velocity and $\\sim 232.5337 \\times M\_{☉}$ for mass

# Checklist

Here is a list of what we need to fully reproduce the article:

- [x] N-body simulation (simple version)
- [ ] Comparison with other methods (in process)
- [ ] Nbody6 (simple run)
- [ ] Gravitational waves
- [ ] Black hole mergers
