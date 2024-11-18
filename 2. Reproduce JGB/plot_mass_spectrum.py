"""Plot mass spectrum for a given NEMO snapshot."""

import os
import subprocess
import typing
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from create_ic import check_parameters
from create_ic import create_argparse
from create_ic import mass_pdf


def mass_spectrum_by_snap(
    filename: typing.Union[str, os.PathLike, Path],
    t: typing.Union[float, str],
) -> np.array:
    """Get a np.array with particles for a given snapshot and time."""
    filename = str(filename)

    snapfile = filename.replace(".nemo", f"{t}.txt")

    if os.path.exists(snapfile):
        os.remove(snapfile)

    command = f"s2a in={filename} out={snapfile} times={t}"
    subprocess.check_call(command, shell=True)

    return np.loadtxt(snapfile).T


if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots mass spectrum for a given snapshot"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file used for density profile computation",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        type=float,
        required=True,
        help="Which times to use. Example: '--times 0.0 0.5 1.0'",
    )
    args = parser.parse_args()

    check_parameters(args)  # sanity checks

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")
    save_dir = filename.absolute().parent

    # Plot original spectrum
    r = np.logspace(-2, 2)
    plt.plot(r, mass_pdf(r, mu=args.mu, scale=args.scale, sigma=args.sigma))

    for t in args.times:
        prof = mass_spectrum_by_snap(
            filename=filename,
            t=t,
        )
        masses = prof[0]

        (counts, bins) = np.histogram(masses, bins=r, density=True)
        plt.hist(bins[:-1], bins, weights=counts, label=f"prof_{t}", histtype="step")

    plt.xscale("log")
    plt.legend()
    plt.show()
