# About

These experiments reproduce a motion of stellar cluster in tidal field.

Before running experiments, do this:

- Start NEMO:

  ```bash
  source start_nemo.sh
  ```

- Go to experiment root:

  ```bash
  cd /path/to/Nbody/03_Globular_cluster/
  ```

# Experiments

## Experiment 1

This experiment is based on an example from the official Nbody6 repository ([source](https://github.com/nbodyx/Nbody6/blob/master/Docs/input)). It is suitable for standard NBODY6 (no GPU). No stellar evolution is taken into account.

Parameters of stellar system:

- 5000 particles
- Plummer distribution (standard notation $r=1$, $M\_{tot}=1$)
- Salpeter IMF ($\\alpha=2.35$)
  - $M\_{low} = 0.2 M\_{☉}$
  - $M\_{high} = 10 M\_{☉}$
- Solar neighbor tidal field (linear approximation), see `xtrnl0.f` for details

1. Run these commands to reproduce:

   ```bash
   cd nbody6_salpeter
   nbody6 < input 1> exp.out 2> exp.err
   u3tos OUT3 OUT3.snap
   cd ..
   ```

1. To make sure that snapshot masses have Salpeter distribution:

   1. Scale snapshot using `M*, R*, V*` from `exp.out`:

      ```bash
      cd nbody6_salpeter
      u3tos OUT3 OUT3.snap
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

   1. Use generated file for nbody6:

      ```bash
      cp outdir/fort.10 reproduce_astro/
      cd reproduce_astro
      nbody6 < input 1> exp.out 2> exp.err
      ```

   The new input file contains options like `KZ(20)=0` and `KZ(22)=-1`. It's strange, but astrophysical units don't work at the moment!

1. Try to feed the same data in any units with `G=1`:

   1. Get `fort.10` in these units:

      ```bash
      cd nbody6_salpeter
      snapscale OUT3_scaled.snap OUT3_g1.snap  mscale=4.300451321727918e-03  # ~232 Msun, km/s and pc, G=1
      runbody6 OUT3_g1.snap outdir_g1 tcrit=0 nbody6=1 exe=nbody6
      ```

   1. Use generated file for nbody6:

      ```bash
      cp outdir_g1/fort.10 reproduce_g1/
      cd reproduce_g1
      nbody6 < input 1> exp.out 2> exp.err
      ```

      The new input file contains options like `KZ(20)=0` and `KZ(22)=2` (for scaling).

# Useful links

- Repositories:
  - https://github.com/nbodyx/Nbody6 (note NEMO uses the official version from `ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz` by Sverre Aarseth)
  - https://github.com/nbodyx/Nbody6ppGPU (version used in NEMO, but not supported by developers now)
  - https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing (supported by developers at the moment)
