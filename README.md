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
git clone https://github.com/teuben/nemo  # I use commit 8a2cbf4fcd565d7a55403ba135fd64716ef0b812
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
> Alternatively, you might want to add the command above (with the full path to `nemo_start.sh`) at the end of your `.bashrc` file.

For more info about NEMO see [NEMO's official documentation](https://astronemo.readthedocs.io/en/latest/) and [NEMO's github pages](https://teuben.github.io/nemo/)

## Install Agama

Activate conda environment, if it is not activated:

```bash
conda activate agama
```

To install Agama, follow these steps:

```bash
git clone https://github.com/GalacticDynamics-Oxford/Agama.git  # I use commit acf08a656e2aa67d466cafd7c92ba2cd277ff9e8
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
├── sandbox
├── images
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
