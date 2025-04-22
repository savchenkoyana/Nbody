# About

These experiments reproduce a motion of stellar cluster in a tidal field. We use Nbody6 (without GPU and MPI, single-thread version introduced by Aarseth).

Before running the experiments, do this:

- Start NEMO:

  ```bash
  source start_nemo.sh
  ```

- Go to experiment root:

  ```bash
  cd /path/to/Nbody/sandbox/nbody6_own_data/
  ```

# Experiments

## Salpeter IMF

This experiment is based on an example from the official Nbody6 repository ([source](https://github.com/nbodyx/Nbody6/blob/master/Docs/input)). It is suitable for standard NBODY6 (no GPU). No stellar evolution is taken into account.

Parameters of stellar system:

- 5000 particles
- Plummer distribution (standard notation $r=1$, $M\_{tot}=1$)
- Salpeter IMF ($\\alpha=2.35$)
  - $M\_{low} = 0.2 M\_{☉}$
  - $M\_{high} = 10 M\_{☉}$
- Solar neighbor tidal field (linear approximation), see `xtrnl0.f` for details

Steps to reproduce the experiment:

1. Create snapshot with Salpeter IMF cluster evolution:

   ```bash
   cd nbody6_salpeter
   nbody6 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=6
   ```

1. To make sure that snapshot masses have the Salpeter distribution:

   1. Scale snapshot using `M*, R*, V*` from `exp.out`:

      ```bash
      snapscale OUT3.snap OUT3_scaled.snap rscale=<R*> vscale=<V*> mscale=<M*>
      snaptrim OUT3_scaled.snap OUT3_scaled_t0.snap times=0
      cd ..
      ```

   1. Run notebook [Salpeter.ipynb](Salpeter.ipynb)

1. Try to feed the same data in astrophysical units (pc, km/s and $M\_{☉}$):

   1. Get data file in Fortran format (`fort.10` file):

      ```bash
      cd nbody6_salpeter
      runbody6 OUT3_scaled_t0.snap outdir tcrit=0 nbody6=1 exe=nbody6
      ```

   1. Use the generated file for nbody6:

      ```bash
      cp outdir/fort.10 reproduce_astro/
      cd reproduce_astro
      nbody6 < input 1> exp.out 2> exp.err
      u3tos OUT3 OUT3.snap mode=6
      cd ..
      ```

   The new input file contains options like `KZ(20)=0` and `KZ(22)=-1`. It's strange, but astrophysical units don't work at the moment!

1. Try to feed the same data in any units with `G=1`:

   1. Get `fort.10` in these units:

      ```bash
      snapscale OUT3_scaled.snap OUT3_g1.snap  mscale=4.300451321727918e-03  # ~232 Msun, km/s and pc, G=1
      runbody6 OUT3_g1.snap outdir_g1 tcrit=0 nbody6=1 exe=nbody6
      ```

   1. Use the generated file for nbody6:

      ```bash
      cp outdir_g1/fort.10 reproduce_g1/
      cd reproduce_g1
      nbody6 < input 1> exp.out 2> exp.err
      u3tos OUT3 OUT3.snap mode=6
      cd ../..  # back to experiment root
      ```

      The new input file contains options like `KZ(20)=0` and `KZ(22)=2` (for scaling).

1. Compare lagrange radius 50% for all three experiments:

   ```bash
   cd ../../02_Reproduce_JGB
   python plot_lagrange_radius.py --nemo-files ../sandbox/nbody6_own_data/nbody6_salpeter/OUT3.snap ../sandbox/nbody6_own_data/nbody6_salpeter/reproduce_astro/OUT3.snap ../sandbox/nbody6_own_data/nbody6_salpeter/reproduce_g1/OUT3.snap --remove-outliers
   cd -
   ```

## Use your own data

This experiment shows evolution of cluster with lognormal IMF. I took `Docs/input` as an example and slightly modified it to reach the end of the simulation (see `input`).

The next step is to run with your own data:

1. Create IC:

   ```bash
   cd ../../02_Reproduce_JGB
   python create_ic.py --mu 0 --sigma 1.5 --scale 1 --r 10 --N 500
   snapscale snap_mu0.0_s1.0_sigma1.5_r10.0_N500/IC.nemo snap_mu0.0_s1.0_sigma1.5_r10.0_N5000/IC_g1.nemo mscale=4.300451321727918e-03  # ~232 Msun, km/s and pc, G=1
   cp snap_mu0.0_s1.0_sigma1.5_r10.0_N500/IC_g1.nemo ../sandbox/nbody6_own_data/nbody6_input/
   ```

1. Check parameters of your snapshot:

   ```bash
   python scale.py --nemo-files snap_mu0.0_s1.0_sigma1.5_r10.0_N500/IC_g1.nemo --length 0.001 --mass 1 --velosity 1  # these are snapshot units in Agama notation
   ```

   There will be `Rbar`, `Zmbar` and `Q` shown in the script output.

1. Prepare `fort.10` for the experiment:

   ```bash
   cd ../sandbox/nbody6_own_data/nbody6_input
   runbody6 IC_g1.nemo outdir tcrit=0 nbody6=1 exe=nbody6
   ```

1. Modify parameters for `Rbar`, `Zmbar` and `Q` from `input`. You can check yourself by running:

   ```bash
   cd -
   python parse_config.py --filename ../sandbox/nbody6_own_data/nbody6_input/input --version nbody6
   cd -
   ```

1. Run simulation:

   ```bash
   nbody6 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=6
   cd ..
   ```

# Useful links

- Repositories:
  - https://github.com/nbodyx/Nbody6 (note NEMO uses the official version from `ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz` by Sverre Aarseth)

# Other

- Note that Nbody6 input file may have two indentical lines at the end:

  ```bash
  20000.0 2 0
  20000.0 2 0
  ```

  Those lines are needed for reading `CLIGHT` (`Ncode/brake4.f`) and `Clight, NBH, IDIS` (`ARchain/chain.f`).

- There are input files for Nbody6 (`input` and `inlog`). These two are almost identical to the ones from official repository, but slightly modified by me to reach the end of the simulation.
