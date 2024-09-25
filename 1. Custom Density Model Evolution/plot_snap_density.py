"""Plot density for a given NEMO snapshot."""

import argparse
import math
import os
import shutil
import subprocess
import sys
import typing
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from create_ic import rho_bh
from create_ic import rho_dm


def profile_by_snap(
    filename: typing.Union[str, os.PathLike],
    t: typing.Union[float, str],
):
    """Get a np.array with density profile for a given snapshot and time."""
    filename = str(filename)
    manipfile = filename.replace(".nemo", "_sphereprof") + str(t)

    if os.path.exists(manipfile):
        os.remove(manipfile)

    command = f'manipulate in={filename} out=. manipname=sphereprof manippars="" manipfile={manipfile} times={t} | tee sphereprof_log 2>&1'
    subprocess.check_call(command, shell=True)

    return np.loadtxt(manipfile).T


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--density-type",
        type=str,
        required=True,
        choices=["BH", "DM"],
        help="Whether to use black hole (BH) density or dark matter (DM) density",
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file used to plot density profile",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        type=float,
        required=True,
        help="Which times to use. Example: '--times 0.0 0.5 1.0'",
    )
    args = parser.parse_args()

    if args.density_type == "BH":
        density_function = rho_bh
    elif args.density_type == "DM":
        density_function = rho_dm
    else:
        raise RuntimeError(f"Unknown density type {args.density_type}")

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")

    # Plot original density
    r = np.logspace(-4, 2)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, density_function(xyz), linestyle="dotted", label="original density")

    plt.xlabel("r")
    plt.ylabel(r"$\rho$")
    plt.xscale("log")
    plt.yscale("log")

    for t in args.times:
        prof = profile_by_snap(
            filename=filename,
            t=t,
        )
        x, y = prof[0], prof[1]
        plt.plot(x, y, label=f"prof_{t}")

    plt.legend()
    plt.show()
