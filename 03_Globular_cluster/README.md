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

This example is taken from official Nbody6 repository ([source](https://github.com/nbodyx/Nbody6/blob/master/Docs/input)). It is suitable for standard NBODY6 (no GPU) or sse. No stellar evolution is taken into account.

Parameters of stellar system:

- 500 particles
- Plummer distribution ($r=1$, $M\_{tot}=1$)
- Eggleton IMF ($M\_{low} = 0.2 M\_{☉}$, $M\_{high} = 10 M\_{☉}$, $f(M) = \\frac{0.19 * M}{(1-M)^0.75 + 0.032\*(1-M)^0.25}$ (in $M\_{☉}$ units), see `imf2.f` for details
- Masses scaled so that $M^{bar}=1$

Parameter of external force: lineralized, Solar tidal field

Run this command to reproduce:

```bash
cd nbody6_simple_exp
nbody6 < input 1> exp.out 2> exp.err
cd ..
```
