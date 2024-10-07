"""Plot virial ratio for a given directory."""

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Directory with `vir_*` files",
    )
    parser.add_argument(
        "--tmax",
        type=float,
        default=20.0,
        help="Max time (in N-body unints). Default: 20.0",
    )
    parser.add_argument(
        "--tstep",
        type=float,
        default=0.25,
        help="Time step (in N-body unints). Default: 0.25",
    )
    args = parser.parse_args()

    save_dir = args.dir

    if not os.path.exists(save_dir):
        raise RuntimeError(f"Directory {save_dir} does not exist")
    if not os.path.isdir(save_dir):
        raise RuntimeError(f"{save_dir} is not a directory")

    vir_files = [f for f in os.listdir(save_dir) if f.startswith("vir_")]

    plt.xlabel("time")
    plt.ylabel("-2T/W")

    for f in vir_files:
        filename = os.path.join(save_dir, f)
        data = np.loadtxt(filename).T

        if f == "vir_IC":
            x = np.arange(0, args.tmax, args.tstep)
            y = np.ones_like(x) * data[1]
            plt.plot(x, y, linestyle="--", label=f)
        else:
            plt.plot(data[0], data[1], linestyle="--", marker="o", label=f)

    plt.legend()
    plt.show()
