# About

This repository contains astrophysical N-body simulation experiments.

# Installation

## Create Conda environment

First prepare an environment. I used conda environment with Python 3.9:

```bash
conda create -n agama python=3.9
```

Clone this repository and install all required packages in the environment:

```bash
git clone https://github.com/savchenkoyana/Nbody.git
cd Nbody
conda activate agama
pip install -r requirements.txt
pre-commit install  # optional, only if you want to commit to repository
```

## Install NEMO

To install NEMO, follow these steps:

```bash
git clone https://github.com/teuben/nemo
cd nemo
./configure --with-yapp=pgplot
make build check bench5
cd ../  # back to repository root
```

If installation completed successfully, you should get "TESTSUITE: OK" for each test (see file `install.log`).

> **Note:** Everytime you want to use NEMO, you first need to execute this from `nemo` repository root:
>
> ```bash
> source nemo_start.sh
> ```
>
> Alternatively, you might want to add the command above (with the full path to `nemo_start.sh`) at the end of your `~/.bashrc` file.

For more info about NEMO see [NEMO's official documentation](https://astronemo.readthedocs.io/en/latest/) and [NEMO's github pages](https://teuben.github.io/nemo/)

## Install Nbody6++GPU

### Install Nbody6++GPU (beijing version)

```bash
git clone git@github.com:nbody6ppgpu/Nbody6PPGPU-beijing
cd Nbody6PPGPU-beijing
./configure --enable-mcmodel=large --with-par=b1m --disable-gpu --disable-mpi  # configuration to quick-start on your computer
make clean
make -j
cd -
```

Add this at the end of your `~/.bashrc` file (and then run `source ~/.bashrc` if you need it in the current session):

```bash
export OMP_STACKSIZE=4096M
ulimit -s unlimited
export OMP_NUM_THREADS=8  # feel free to change
```

Feel free to alter `OMP_NUM_THREADS` as you wish.

The resulting binary can be found here: `Nbody6PPGPU-beijing/build/nbody6++.*`

### Install Nbody6++GPU (original version)

The reason why we may need two versions of Nbody6++GPU is that the one ending with `-beijing` is supported at the moment, but the original one has useful features not implemented in the current version.

```bash
git clone https://github.com/nbodyx/Nbody6ppGPU.git
cd Nbody6ppGPU
export FCFLAGS='-fallow-argument-mismatch'
./configure --enable-mcmodel=large --with-par=b1m --disable-gpu --disable-mpi --enable-tools --prefix=$HOME  # there is also `--enable-tt`, not tested by me yet
make clean
make
make install
cd -
```

The resulting binary can be found here: `Nbody6ppGPU/build/nbody6++.*`

## Install Agama

Activate conda environment, if it is not activated:

```bash
conda activate agama
```

To install Agama, follow these steps:

```bash
git clone https://github.com/GalacticDynamics-Oxford/Agama.git
cd Agama
pip install .
cd ../  # back to repository root
```

For more info about Agama see https://arxiv.org/pdf/1802.08239 and official [AGAMA documentation](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/doc/reference.pdf).

## Install glnemo2 (optional)

To install `glnemo2` for snapshot visualization, follow the instructions at [the official site](https://projets.lam.fr/projects/glnemo2/wiki/download).

After installation, you will have the following repository structure:

```bash
Nbody
├── Agama  # Agama repository root
├── nemo  # nemo repository root
├── Nbody6PPGPU-beijing  # Nbody6++GPU repository root
├── sandbox  # dir for simple and small experiments
├── images  # images needed for md-files
├── README.md
├── requirements.txt
├── ...  # other files
```

# Experiments

### 1. Custom Density Model Evolution

This experiment demonstrates how to create a self-consistent model for a custom density function.
This is just a toy example based on [https://arxiv.org/pdf/1807.06590](https://arxiv.org/pdf/1807.06590)
For more info see [README](01_Custom_Density_Model_Evolution/README.md)

### 2. Reproduce JGB

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido.
The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.
For more info see [README](02_Reproduce_JGB/README.md)

### 3. Globular cluster

The goal of this experiment is to reproduce a motion of globular cluster in Galaxy's tidal field using existing N-body codes. For more info see [README](03_Globular_cluster/README.md)
