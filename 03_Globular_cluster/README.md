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

This example is taken from official Nbody6 repository ([source](https://github.com/nbodyx/Nbody6/blob/master/Docs/input)). It is suitable for standard NBODY6 (no GPU). No stellar evolution is taken into account.

Parameters of stellar system:

- 500 particles
- Plummer distribution ($r=1$, $M\_{tot}=1$)
- Eggleton IMF, see `imf2.f` for details
  - $M\_{low} = 0.2 M\_{☉}$
  - $M\_{high} = 10 M\_{☉}$
  - $f(M) = \\frac{0.19 * M}{(1-M)^{0.75} + 0.032\*(1-M)^{0.25}}$ (in $M\_{☉}$ units)
- Masses scaled so that $M^{bar}=1$

Parameter of external force:

- Solar neighbor tidal field (linear approximation), see `xtrnl0.f` for details

Run this command to reproduce:

```bash
cd nbody6_simple_exp
nbody6 < input 1> exp.out 2> exp.err
u3tos OUT3 OUT3.snap
cd ..
```

## Experiment 2

This example is taken from official Nbody6++GPU documentation (with minimal modifications).

Parameters of stellar system:

- 16000 particles
- Plummer distribution ($r=$, $M\_{tot}=$)
- Kroupa IMF, see `imf2.f` for details
  - $M\_{low} = 0.08 M\_{☉}$
  - $M\_{high} = 20 M\_{☉}$

Stellar evolution is switched, initial metallicity 0.001. Multiples and chain regularization are switched on.

Parameter of external force:

- Solar neighbor tidal field (linear approximation), see `xtrnl0.f` for details

Run this command to reproduce:

```bash
cd nbody6++example
nbody6 < input 1> exp.out 2> exp.err
u3tos OUT3 OUT3.snap
cd ..
```

<!-- - Bulge (~1 kpc, $10^{10} M\_{☉}$, spherical potentail such as Hernquist or Plummer). Represents the dense central region of the galaxy.

- Disk (radial ~3 kpc, vertical ~300 pc, $5\times 10^{10} M\_{☉}$, flattented potential such as Miyamoto–Nagai potential)

- Halo (virial radius ~200 kpc, $10^{12} M\_{☉}$, logarithmic or Navarro–Frenk–White (NFW) profiles). This component dominates at large radii and is critical for explaining the flat rotation curve of the Milky Way.
 -->

# Useful links

- Repositories:
  - https://github.com/nbodyx/Nbody6
  - https://github.com/nbodyx/Nbody6ppGPU
  - https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing
