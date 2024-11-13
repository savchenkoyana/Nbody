# About

This repository contains astrophysical N-body simulation experiments.

# Installation

## Create Conda environment

First prepare an environment. I used conda environment with Python 3.9:

```shell
conda create -n agama python=3.9
```

Clone this repository and install all required packages in the environment:

```shell
git clone https://github.com/savchenkoyana/Nbody.git
cd Nbody
conda activate agama
pip install -r requirements.txt
pre-commit install  # optional, only if you want to commit to repository
```

## Install NEMO

To install NEMO, follow these steps:

```shell
git clone https://github.com/teuben/nemo
cd nemo
./configure --with-yapp=pgplot
make build check bench5
cd ../  # back to repository root
```

If installation completed successfully, you should get "TESTSUITE: OK" for each test (see file `install.log`).

> **Note:** Everytime you want to use NEMO, you first need to execute this from `nemo` repository root:
>
> ```shell
> source nemo_start.sh
> ```
>
> Alternatively, you might want to add the command above (with the full path to `nemo_start.sh`) at the end of your `.bashrc` file.

## Install Agama

Activate conda environment, if it is not activated:

```shell
conda activate agama
```

To install Agama, follow these steps:

```shell
git clone https://github.com/GalacticDynamics-Oxford/Agama.git
cd Agama
pip install .
cd ../  # back to repository root
```

For more info about Agama see https://arxiv.org/pdf/1802.08239 and official [AGAMA documentation](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/doc/reference.pdf).

# Experiments

### 1. Custom Density Model Evolution

This experiment demonstrates how to create a self-consistent model for a custom density function.
This is just a toy example based on [https://arxiv.org/pdf/1807.06590](https://arxiv.org/pdf/1807.06590)
For more info see [README](1.%20Custom%20Density%20Model%20Evolution/README.md)

### 2. Reproduce JGB

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido.
The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.
For more info see [README](2.%20Reproduce%20JGB/README.md)
