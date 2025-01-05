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
git clone https://github.com/teuben/nemo  # I use commit 8a2cbf4fcd565d7a55403ba135fd64716ef0b812
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

For more info about NEMO see [NEMO's official documentation](https://astronemo.readthedocs.io/en/latest/) and [NEMO's github pages](https://teuben.github.io/nemo/)

## Install Nbody6

To install Nbody6, follow these steps:

```shell
wget ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz
mkdir nbody6
gunzip nbody6.tar.gz
tar -xf nbody6.tar -C nbody6
(cd nbody6/GPU2 ;  make clean; make sse ; cp run/nbody7b.sse $NEMOBIN)
(cd nbody6/Ncode ; make clean; make     ; cp nbody6         $NEMOBIN)
```

Check that everything works fine:

```shell
bash test_runbody6.sh
```

## Install Agama

Activate conda environment, if it is not activated:

```shell
conda activate agama
```

To install Agama, follow these steps:

```shell
git clone https://github.com/GalacticDynamics-Oxford/Agama.git  # I use commit acf08a656e2aa67d466cafd7c92ba2cd277ff9e8
cd Agama
pip install .
cd ../  # back to repository root
```

For more info about Agama see https://arxiv.org/pdf/1802.08239 and official [AGAMA documentation](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/doc/reference.pdf).

## Install glnemo2 (optional)

To install `glnemo2` for snapshot visualization, follow the instructions at [the official site](https://projets.lam.fr/projects/glnemo2/wiki/download).

After installation, you will have the following repository structure:

```shell
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
For more info see [README](1.%20Custom%20Density%20Model%20Evolution/README.md)

### 2. Reproduce JGB

This experiment is based on article [Primordial Black Hole clusters, phenomenology & implications](https://arxiv.org/pdf/2405.06391v1) by Juan Garcia-Bellido.
The goal of this experiment is to create a self-consistent model with Plummer density profile and log-normal mass spectrum, and then evolve it for Hubble time.
For more info see [README](2.%20Reproduce%20JGB/README.md)
