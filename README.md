# About

This repository contains astrophysical N-body simulation experiments.

# Installation

Clone this repository and `cd` to its root:

```bash
git clone https://github.com/savchenkoyana/Nbody.git
cd Nbody
```

At the end of the Installation step you will get the following repository structure:

```bash
Nbody
├── Agama                # Agama repository root
├── nemo                 # nemo repository root
├── Nbody6PPGPU-beijing  # Nbody6++GPU (Beijing version) repository root
├── Nbody6ppGPU          # Nbody6++GPU (original version) repository root
├── sandbox              # dir for simple and small experiments
├── images               # images needed for md-files
├── README.md
├── requirements.txt
├── ...                  # other files
```

Don't skip any steps if they are not marked as optional!

## Install MESA SDK

[MESA SDK](http://user.astro.wisc.edu/~townsend/static.php?ref=mesasdk) helps to deal with incompatibilities and bugs in compilers and libraries.

- Check that all pre-requisites are installed

- Download latest `tar.gz` archive for Linux into `~/`

- Unzip via `tar xzf mesasdk*.tar.gz`

- Add something like this at the end of your `~/.bashrc` file:

  ```bash
  export MESASDK_ROOT=~/mesasdk;
  source $MESASDK_ROOT/bin/mesasdk_init.sh
  ```

- Run in current terminal session:

  ```bash
  source ~/.bashrc
  ```

## Install NEMO

NEMO is a useful package with tools for data analysis. There are also some N-body simulation methods implemented in NEMO, such as gyrFalcON, Nbody0, Nbody1, Nbody2 and Nbody4. For more info about NEMO see [NEMO's official documentation](https://astronemo.readthedocs.io/en/latest/) and [NEMO's github pages](https://teuben.github.io/nemo/)

- To install NEMO, follow these steps:

  ```bash
  git clone https://github.com/teuben/nemo
  cd nemo
  ./configure --with-yapp=pgplot
  make build check bench5
  cd ../  # back to repository root
  ```

- If installation completed successfully, you should get "TESTSUITE: OK" for each test (see file `install.log`).

- Add something like this at the end of your `~/.bashrc` file:

  ```bash
  source nemo_start.sh
  ```

- Run in current terminal session:

  ```bash
  source ~/.bashrc
  ```

## Install Nbody6++GPU

Nbody6++GPU is state-of-the-art method for cluster simulations.

### Install Beijing version (supported now)

The installation of Nbody6++GPU-beijing is a little bit tricky. The reason is that we need hdf5 files as outputs as they are easily parsed with python, but the automatic makefile generation with `--enable-hdf5` option is broken at the moment. So you first need to configure `Makefile` _without_ hdf5 and then edit it.

- First configure Makefile without hdf5:

  ```bash
  git clone git@github.com:nbody6ppgpu/Nbody6PPGPU-beijing
  cd Nbody6PPGPU-beijing
  ./configure --enable-mcmodel=large --with-par=b1m --disable-gpu --disable-mpi  # configuration to quick-start on your computer
  ```

- Edit `build/Makefile` (lines 25-30):

  ```makefile
  HDF5_FLAGS = -D H5OUTPUT -I${MESASDK_ROOT}/include -L${MESASDK_ROOT}/lib -lhdf5_fortran -lhdf5  # instead of HDF5_FLAGS = -D H5OUTPUT
  ...
  FFLAGS = -O3 -fPIC -mcmodel=large -fopenmp -I../include $(MPI_FLAGS) ${SIMD_FLAGS} $(GPU_FLAGS) ${OMP_FLAGS} ${HDF5_FLAGS}  # add ${HDF5_FLAGS} at the end
  ```

- And finally, run installation:

  ```bash
  make clean
  make -j
  cd ../  # back to repository root
  ```

- Add this at the end of your `~/.bashrc` file:

  ```bash
  export OMP_STACKSIZE=4096M
  ulimit -s unlimited
  export OMP_NUM_THREADS=8  # feel free to change
  ```

  Feel free to alter `OMP_NUM_THREADS` as you wish.

- Run in current terminal session:

  ```bash
  source ~/.bashrc
  ```

The resulting binary can be found here: `Nbody6PPGPU-beijing/build/nbody6++.*`

### Install original version

```bash
git clone https://github.com/nbodyx/Nbody6ppGPU.git
cd Nbody6ppGPU
export FCFLAGS='-fallow-argument-mismatch'
./configure --enable-mcmodel=large --with-par=b1m --disable-gpu --enable-tools  # there is also `--enable-tt`, not tested by me yet
make clean
make -j
cd ../  # back to repository root
```

The resulting binary can be found here: `Nbody6ppGPU/build/nbody6++.*`

## Create Conda environment for Agama

I used conda environment with Python 3.9:

```bash
conda create -n agama python=3.9
```

Install all required packages into the environment:

```bash
conda activate agama
pip install -r requirements.txt
pre-commit install  # optional, only if you want to commit to repository
python -m pip install --only-binary galpy galpy  # tool for galactic dynamics, see https://docs.galpy.org/
python -m pip install --no-binary=h5py h5py  # tool for parsing simulation data with python, see https://docs.h5py.org/en/stable/quick.html
```

To install Agama, follow these steps (with activated `agama` environment!):

```bash
git clone https://github.com/GalacticDynamics-Oxford/Agama.git
cd Agama
pip install .
cd ../  # back to repository root
```

For more info about Agama see https://arxiv.org/pdf/1802.08239 and official [AGAMA documentation](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/doc/reference.pdf).

## Install glnemo2 (optional)

To install `glnemo2` for snapshot visualization, follow the instructions at [the official site](https://projets.lam.fr/projects/glnemo2/wiki/download).

# Experiments

### 1. Custom Density Model Evolution

This experiment demonstrates how to create a self-consistent model for a custom density function.
This is just a toy example based on [https://arxiv.org/pdf/1807.06590](https://arxiv.org/pdf/1807.06590)
For more info see [README](01_Custom_Density_Model_Evolution/README.md)

### 2. Reproduce JGB

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1).
The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.
For more info see [README](02_Reproduce_JGB/README.md)

### 3. PBH cluster in Milky Way potential

The goal of this experiment is to simulate a PBH cluster with different IC.
See [README](03_MW_PBH_cluster/README.md) for more details.
