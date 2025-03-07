# About

These experiments reproduce a motion of stellar cluster in tidal field.

How to reproduce:

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
- Plummer distribution (standart notation $r=1$, $M\_{tot}=1$)
- Salpeter IMF ($\\alpha=2.35$)
  - $M\_{low} = 0.2 M\_{☉}$
  - $M\_{high} = 10 M\_{☉}$

Parameter of external force:

- Solar neighbor tidal field (linear approximation), see `xtrnl0.f` for details

Run this command to reproduce:

```bash
cd nbody6_salpeter
nbody6 < input 1> exp.out 2> exp.err
u3tos OUT3 OUT3.snap
cd ..
```

To make sure that snapshot masses have Salpeter distribution:

1. Scale snapshot using `M*, R*, V*` from `exp.out`:

   ```bash
   cd nbody6_salpeter
   snapscale OUT3.snap OUT3_scaled.snap rscale=<R*> vscale=<V*> mscale=<M*>
   cd ..
   ```

1. Run notebook [Salpeter.ipynb](Salpeter.ipynb)

To feed scaled data in physical units:

1. Get data file in Fortran format (`fort.10` file):

   ```bash
   cd nbody6_salpeter
   runbody6 OUT3_scaled.snap outdir tcrit=1 nbody6=1 exe=nbody6
   ```

1. Use generated `outdir/fort.10` for nbody6:

   ```bash
   cp outdir/fort.10 reproduce/
   cd reproduce
   nbody6 < input 1> exp.out 2> exp.err
   ```

The new input file contains options like `KZ(20)=0` and `KZ(22)=-1`, which ensure that we use data from loaded snapshot. (!!! Needs checking)

<!-- - Bulge (~1 kpc, $10^{10} M\_{☉}$, spherical potentail such as Hernquist or Plummer). Represents the dense central region of the galaxy.

- Disk (radial ~3 kpc, vertical ~300 pc, $5\times 10^{10} M\_{☉}$, flattented potential such as Miyamoto–Nagai potential)

- Halo (virial radius ~200 kpc, $10^{12} M\_{☉}$, logarithmic or Navarro–Frenk–White (NFW) profiles). This component dominates at large radii and is critical for explaining the flat rotation curve of the Milky Way.
 -->

# Useful links

- Repositories:
  - https://github.com/nbodyx/Nbody6 (note NEMO uses [the official version](ftp://ftp.ast.cam.ac.uk/pub/sverre/nbody6/nbody6.tar.gz) by Sverre Aarseth)
  - https://github.com/nbodyx/Nbody6ppGPU (version used in NEMO, but not supported by developers now)
  - https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing (supported by developers at the moment)
