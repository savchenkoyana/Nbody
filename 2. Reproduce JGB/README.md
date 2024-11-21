# About

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido.

The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.

![](../images/pic2.png)

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

- Create initial coordinates for evolution:

  ```shell
  cd 2.\ Reproduce\ JGB/
  python create_ic.py --mean <MEAN> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS> --N <N>
  ```

  Here `N` is the number of particles in simulation, `MEAN`, `SIGMA`, and `SCALE` are log-normal distribution parameters of PBH mass spectrum, and `PLUMMER_RADIUS` is a characteristic size of Plummer density distribution (type `python create_ic.py --help` for more details).

  The above command will automatically create (or re-create) a directory with name `snap_m<MEAN>_s<SIGMA>_r<PLUMMER_RADIUS>_N<N>` containing file `IC.nemo` with initial coordinates for evolution.

  To reproduce the results from the article, use these parameters combinations:

  | $\\mu$, $M\_{☉}$ | s, $M\_{☉}$ | $\\sigma$ | Plummer radius, pc | Number of particles |
  | ---------------- | ----------- | --------- | ------------------ | ------------------- |
  | 0                | 1           | 0.5       | 10                 | $2 \\times 10^4$    |
  | 0                | 1           | 1         | 10                 | $2 \\times 10^4$    |
  | 0                | 1           | 1.5       | 10                 | $2 \\times 10^4$    |
  | 10               | 1.5         | 0.954     | 10                 | $2 \\times 10^4$    |

- Evolve for a couple of crossing times:

  ```shell
  gyrfalcON in=<DIRNAME>/IC.nemo out=<DIRNAME>/out.nemo eps=<eps> kmax=<kmax> Grav=<Grav> tstop=<tstop> step=<step> logstep=300
  ```

  Here `DIRNAME` is the name of the directory with `IC.nemo`, and `logstep=300` is a parameter which controls console output size. Other parameters such as `<eps>`, `<kmax>` and `<Grav>` should be thoroughly chosen. The previous python script `create_ic.py` prints a set of recommended `gyrfalcON` parameters at the end of the output (don't forget to change `tstop` parameter according to how many crossing times you want to use).

## External potential

This section desctibes how to perform the evolution of PBH cluster in an external potential.

### Milky Way potential

Here I use Milky Way potential created with `Agama` scripts and based on the analytic approximation for the bar model from Portail et al. (2017).

- To create a Milky Way potential for evolution, run:

  ```shell
  cd ../agama/py  # cd to `py` folder in your Agama repository
  python example_mw_potential_hunter24.py  # create Milky Way potential
  cd -
  ```

  This command creates files `MWPotentialHunter24_*.ini` into `Nbody/agama/py` directory. Note that snapshot units and units used to create these potentials differ, so before using them we need to scale snapshot data so that units match.

- Transform snapshot data before evolution in an external potential. This transformation includes:

  - convertion to different physical units by scaling
  - shifting coordinates (we want our PBH clusters to become a satellite rotating around the Milky Way galaxy center)

  Run the transformation script:

  ```shell
  python preprocess_snap.py --nemo-file `DIRNAME`/IC.nemo --r <PLUMMER_RADIUS> --r-shift <x> <y> <z> --v-shift <vx> <vy> <vz>
  ```

  This script will perform the transformations of data as well as printing new parameters for `gyrFalcON` (note that they change because we change units). The resulting snapshot will be stored in `<DIRNAME>/IC_scaled_shifted.nemo`.

  To reproduce [the official example](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/py/example_nbody_simulation.py) from `Agama` repository, use these shifts: `--r-shift 2 0 0 --v-shift 0 -100 50`.

- Run evolution:

  ```shell
  gyrfalcON in=<DIRNAME>/IC_scaled_shifted.nemo out=<DIRNAME>/<OUT_NAME>.nemo eps=<eps> kmax=<kmax> Grav=<Grav> tstop=<tstop> step=<step> logstep=300 accname=agama accfile=../Agama/py/MWPotentialHunter24_rotating.ini
  ```

  We recommend to use parameters provided by `preprocess_snap.py` script for `gyrFalcON`.

### Point mass potential

JGB writes:

> Clusters are themselves immersed in a central gravitational potential with orbital radius $R_c$ = 34 kpc and central mass $M = 4.37 × 10^{10} M\_{☉}$ throughout the entire evolution. This is just a point mass approximation which leads to a circular movement of period T = 2.81 Gyr

The easiest way to implement the motion in this potential is to add a new particle representing the central mass to the existing snapshot with PBH cluster data:

```shell
```

# Explore results

- Visualize cluster evolution:

  ```shell
  snapplot3 <DIRNAME>/out.nemo
  ```

  There is also a possibility to visulaize the evolution using [glnemo2](https://projets.lam.fr/projects/glnemo2/wiki/download).

- Plot mass density $$\\rho(r)$$ for the resulting snapshot and compare with initial density:

  ```shell
  python plot_snap_density.py --nemo-file <DIRNAME>/out.nemo --times <t1> <t2> ... <tn> --mean <MEAN> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS>
  ```

  `<t1> <t2> ... <tn>` means that all timestamps from snapshot that you want to use to plot the graph should be separated by a space.
  E.g., `0.0 1.0 2.0`.

  When you evolve a cluster in its own gravitational field, the final density should look like the initial density. This indicates that your model is truly self-consistent.

- Compute and plot mass spectrum for a given snapshot along with the original distribution function:

  ```shell
  python plot_mass_spectrum.py --nemo-file <DIRNAME>/out.nemo --times <t1> <t2> ... <tn> --mean <MEAN> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS>
  ```

  The resulting histogram (mass distribution from snapshot) and the line plot (original pdf) should look like a log-normal distribution with your parameters. You can compare your results with the picture at the beginning of this README document.
