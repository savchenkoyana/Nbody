# About

This experiments reproduces a motion of stellar cluster in tidal field.

How to reproduce:

- Start NEMO:

  ```bash
   source start_nemo.sh
  ```

- Go to experiment root:

  ```bash
  cd /path/to/Nbody/03_Globular_cluster/
  ```

- Run star cluster simulation with external tidal field:

  ```bash
  cd nbody6_simple_exp
  nbody6 < input 1> exp.out 2> exp.err
  cd ..
  ```

  This example is taken from official Nbody6 repository ([source](https://github.com/nbodyx/Nbody6/blob/master/Docs/input)). It is suitable for standard NBODY6 (no GPU) or sse. No stellar evolution is taken into account.
