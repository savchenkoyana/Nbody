# About

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

- Create initial coordinates of cluster:

  ```bash
  python create_ic.py --mu <MU> --sigma <SIGMA> --scale <SCALE> --r <PLUMMER_RADIUS> --N <N>
  ```

  Here `N` is the number of particles in simulation, `MU`, `SIGMA`, and `SCALE` are log-normal distribution parameters of PBH mass spectrum, and `PLUMMER_RADIUS` is a characteristic size of Plummer density distribution (type `python create_ic.py --help` for more details).

  The above command will automatically create (or re-create) a directory with name `snap_mu<MU>_s<SCALE>_sigma<SIGMA>_r<PLUMMER_RADIUS>_N<N>` containing file `IC.nemo` with initial coordinates for evolution.

- Preprocess data

  To convert data to units with `G=1` (pc, km/s and $\\sim 232.5337 \\times M\_{☉}$), run:

  ```bash
  snapscale in=`DIRNAME`/IC.nemo \
    out=`DIRNAME`/IC_g1.nemo \
    mscale=4.300451321727918e-03
  ```

  For more details see section [Units](#Units).

- Run evolution (TODO)

- Postprocess your data to plot profiles, spectras, etc. (TODO)

# Explore results

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
  python animate.py --nemo-file <DIRNAME>/out_postprocessed.nemo --add-point-source
  ```

## Plot density profile $$\\rho(r)$$

TODO

## Plot Lagrange radii

TODO

You can compare your results with plots from the article:

![](../images/cluster_stat.png)

![](../images/lagrange_radii.png)

Note that Lagrange radius at $t=0$ should be approximately 13 pc according to [analytical expression](https://en.wikipedia.org/wiki/Plummer_model) for Plummer with size 10 pc.

## Plot mass spectrum $$f(M)$$

TODO

# Compare with other N-body methods

The comparison with other methods is descriped in details in [README_NBODY.md](README_NBODY.md).

# Units

We use non-usual units in our experiments:

- We use pc (length), km/s (velocity) and $M\_{☉}$ (mass) units for creating a cluster model because of convenience
- We use units with `G=1` for evolution: pc for lenght, km/s for velocity and $\\sim 232.5337 \\times M\_{☉}$ for mass

# Checklist

Here is a list of what we need to fully reproduce the article:

- [x] Comparison with other methods
- [ ] Nbody6 (simple run)
- [ ] Gravitational waves + Black hole mergers
