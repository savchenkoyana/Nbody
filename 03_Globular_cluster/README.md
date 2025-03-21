# About

These experiments reproduce a motion of stellar cluster in a tidal field.

Before running the experiments, do this:

- Start NEMO:

  ```bash
  source start_nemo.sh
  ```

- Go to experiment root:

  ```bash
  cd /path/to/Nbody/03_Globular_cluster/
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
      snaptrim OUT3.snap - times=0 | snapscale - OUT3_scaled.snap rscale=<R*> vscale=<V*> mscale=<M*>
      cd ..
      ```

   1. Run notebook [Salpeter.ipynb](Salpeter.ipynb)

1. Try to feed the same data in astrophysical units (pc, km/s and $M\_{☉}$):

   1. Get data file in Fortran format (`fort.10` file):

      ```bash
      cd nbody6_salpeter
      runbody6 OUT3_scaled.snap outdir tcrit=0 nbody6=1 exe=nbody6
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
   cd ../02_Reproduce_JGB
   python plot_lagrange_radius.py --nemo-files ../03_Globular_cluster/nbody6_salpeter/OUT3.snap  ../03_Globular_cluster/nbody6_salpeter/reproduce_astro/OUT3.snap ../03_Globular_cluster/nbody6_salpeter/reproduce_g1/OUT3.snap --remove-outliers
   cd -
   ```

## Lognormal IMF

This experiment shows an evolution of cluster with lognormal IMF.

1. Create IC for lognormal spectra:

   ```bash
   cd ../02_Reproduce_JGB
   python create_ic.py --mu 0 --sigma 1.5 --scale 1 --r 10 --N 5000
   snapscale snap_mu0.0_s1.0_sigma1.5_r10.0_N5000/IC.nemo snap_mu0.0_s1.0_sigma1.5_r10.0_N5000/IC_g1.nemo mscale=4.300451321727918e-03  # ~232 Msun, km/s and pc, G=1
   cp snap_mu0.0_s1.0_sigma1.5_r10.0_N5000/IC_g1.nemo ../03_Globular_cluster/nbody6_lognormal/
   ```

1. Prepare `fort.10` for the experiment:

   ```bash
   cd ../03_Globular_cluster/nbody6_lognormal
   runbody6 IC_g1.nemo outdir tcrit=0 nbody6=1 exe=nbody6
   ```

1. Run simulation in a standard tidal field:

   ```bash
   cp outdir/fort.10 standard/
   cd standard
   nbody6 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=6
   cd ..
   ```

1. Run simulation in a point-mass field of SMBH (compare with JGB):

   ```bash
   cp outdir/fort.10 point_mass/
   cd point_mass
   nbody6 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=6
   cd ..
   ```

1. Try the same with `Nbody4`:

   ```bash
   cd ../nbody4_lognormal
   cp ../nbody6_lognormal/outdir/fort.10 standard/
   cd standard
   nbody4 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=4
   cd ..
   ```

   and

   ```bash
   cp ../nbody6_lognormal/outdir/fort.10 point_mass/
   cd point_mass
   nbody4 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=4
   cd ..
   ```

1. Run these experiments with other IMFs (for example, with Salpeter IMF) and compare results:

   ```bash
   cd ../nbody4_salpeter
   cp ../nbody6_salpeter/outdir/fort.10 standard/
   cd standard
   nbody4 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=4
   cd ..
   ```

   and

   ```bash
   cp ../nbody6_salpeter/outdir/fort.10 point_mass/
   cd point_mass
   nbody4 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap mode=4
   cd ..
   ```

1. Plot the results:

   ```bash
   cd ../../02_Reproduce_JGB
   python plot_lagrange_radius.py --nemo-files ../03_Globular_cluster/nbody4_lognormal/standard/OUT3.snap  ../03_Globular_cluster/nbody4_lognormal/point_mass/OUT3.snap ../03_Globular_cluster/nbody6_lognormal/standard/OUT3.snap ../03_Globular_cluster/nbody6_lognormal/point_mass/OUT3.snap  --remove-outliers --sigma 1.5 --dens-par 500
   ```

# Useful links

- Repositories:
  - https://github.com/nbodyx/Nbody6 (note NEMO uses the official version from `ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz` by Sverre Aarseth)
  - https://github.com/nbodyx/Nbody6ppGPU (version used in NEMO, but not supported by developers now)
  - https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing (supported by developers at the moment)
