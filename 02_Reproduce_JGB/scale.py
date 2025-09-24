"""Print statistics for a given NEMO snapshot."""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Union

import agama
import numpy as np
from utils.snap import remove


def get_scaling(filename, current_units):
    agama.setUnits(**current_units)

    xv, m = agama.readSnapshot(filename)
    pos = xv[:, :3]
    vel = xv[:, 3:]
    N = m.shape[0]

    # --- Kinetic energy
    v2 = np.sum(vel**2, axis=1)
    T = 0.5 * np.sum(m * v2)

    # --- Potential energy using Agama multipole expansion
    pot = agama.Potential(type="Multipole", particles=(xv, m), symmetry="spherical")
    phi = pot.potential(pos)
    W = 0.5 * np.sum(m * phi)

    # --- Total energy and virial ratio
    E = T + W
    Q = T / abs(W)

    print(f"E = {E}, T = {T}, W = {W}, Q = {Q}")

    M = np.sum(m)
    R = -0.25 * agama.G * M**2 / E

    mscale = 1 / M
    rscale = 1 / R
    vscale = np.sqrt(mscale / rscale / agama.G)

    print(f"mscale={mscale}, rscale={rscale}, vscale={vscale}")
    print(
        f"Rbar(pc)={R * 1e3 * current_units['length']}, "
        f"Zmbar(Msun)={np.mean(m) * current_units['mass']}, Q={Q}"
    )

    scale = {
        "mscale": mscale,
        "rscale": rscale,
        "vscale": vscale,
    }

    units = {
        "mass": current_units["mass"] / mscale,
        "length": current_units["length"] / rscale,
        "velocity": current_units["velocity"] / vscale,
    }
    return units, scale


def scale_snapshot(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rscale: float,
    vscale: float,
    mscale: float,
):
    remove(outfile)

    command = f"snapscale in={filename} out={outfile} rscale={rscale} vscale={vscale} mscale={mscale} | tee snapscale_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program prints statistics for a given NEMO snapshot"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--length", type=float, required=True, help="Length units scale in kpc"
    )
    parser.add_argument(
        "--mass", type=float, required=True, help="Mass units scale in Msun"
    )
    parser.add_argument(
        "--velocity", type=float, required=True, help="Velocity units scale in km/s"
    )
    args = parser.parse_args()

    if not Path(args.nemo_file).exists():
        raise RuntimeError(f"filename {args.nemo_file} does not exist")

    file_extension = os.path.splitext(args.nemo_file)[1]
    outfile = args.nemo_file.replace(file_extension, "_NBODY_UNITS" + file_extension)

    # Compute units
    new_units, scale = get_scaling(
        filename=args.nemo_file,
        current_units={
            "length": args.length,
            "mass": args.mass,
            "velocity": args.velocity,
        },
    )

    # Snapscale
    scale_snapshot(
        filename=args.nemo_file,
        outfile=outfile,
        **scale,
    )

    # Check conversion
    get_scaling(outfile, new_units)
