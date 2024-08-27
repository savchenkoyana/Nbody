# About

This repository containts astrophysical N-body simulation experiments.

# Installation

First prepare an environment. I used conda environment with Python 3.9:

```bash
conda create -n agama python=3.9
```

Activate conda environment and install all required packages:

```bash
conda activate agama
pip install -r requirements.txt
```

Install Agama:

```bash
git clone https://github.com/GalacticDynamics-Oxford/Agama.git  # I used commit hash 294d5a700941c9ee2640a33e99ab877e6213fa6f
cd Agama
pip install --user ./
cd ../
```

# How to reproduce

Before running jupyter notebooks, you may need to create a Milky Way potential:

```bash
python Agama/py/example_mw_potential_hunter24.py
```

# Other

For more info about AGAMA see https://arxiv.org/pdf/1802.08239
