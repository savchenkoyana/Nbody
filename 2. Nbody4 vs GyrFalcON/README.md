# About

The goal of this experiment is to compare slow but precise Aarset `nbody4` with fast but approximate Dehnen `gyrFalcON`.

# How to reproduce

To reproduce the experiment, follow these steps:

- Start Nemo (from `nemo` repository root):
  ```shell
  source start_nemo.sh
  ```
- Go to current directory:
  ```shell
  cd 2.\ Nbody4\ vs\ GyrFalcON/
  ```
- Run evolution for a system with 10000 points distributed with Plummer density for 20 crossing times:
  ```shell
  bash run.sh
  ```
- Compute virial ratio statistics for resulting snapshots:
  ```shell
  bash stat.sh
  ```
- Visualize results:
  ```shell
  python plot_virial_ratio.py --dir nbody4_vs_gyrfalcon
  ```
