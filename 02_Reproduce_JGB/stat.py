"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path

import numpy as np
from colorama import Fore
from colorama import Style
from utils.snap import masses_in_lagrange_radius
from utils.snap import parse_nemo

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program prints statistics for a given NEMO snapshot (beginning and end)."
    )
    parser.add_argument(
        "--nemo-files",
        nargs="+",
        type=str,
        required=True,
        help="Nemo files used for analysis",
    )
    parser.add_argument(
        "--fraction",
        type=float,
        default=0.5,
        help="The fraction of mass used to compute the lagrange radius. Default: 0.5 (half-mass)"
        "Recommended fractions: 0.01,0.03,0.1,0.3,0.5,0.7,0.9,0.97,0.99 "
        "(see https://teuben.github.io/nemo/man_html/lagrange_radii.1.html)",
    )
    parser.add_argument(
        "--dens-parameter",
        type=int,
        default=100,
        help="The number of neighbours in SPH-like estimation for 'dens_centre' manipulator. If 0, density center is not computed. Default: 500",
    )
    parser.add_argument(
        "--store-artifacts",
        action="store_true",
        help="Whether to store NEMO artifacts for debug",
    )
    parser.add_argument(
        "--remove-outliers",
        action="store_true",
        help="Whether to remove outliers from non-converged dense_cluster",
    )
    args = parser.parse_args()

    for i, filename in enumerate(args.nemo_files):
        if not Path(filename).exists():
            raise RuntimeError(f"filename {filename} does not exist")

        print(f"{Fore.GREEN}Filename = {filename}{Style.RESET_ALL}")

        timestamps = np.array(
            [0.0, 12.0 * 1e3, 13.0 * 1e3, 14.0 * 1e3], dtype=np.float32
        )

        for t in timestamps:
            snap = parse_nemo(filename=filename, t=t)  # m, x, y, z, vx, vy, vz

            masses = snap[0]
            N = masses.shape[0]
            m_tot = np.sum(masses)

            try:
                masses, lagrange_r, mask = masses_in_lagrange_radius(
                    filename=filename,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                    dens_par=args.dens_parameter,
                    fraction=args.fraction,
                )
            except RuntimeError:
                if args.remove_outliers:
                    continue
                raise

            print(
                f"{Fore.GREEN}\t t={t} Myr N={N} M={m_tot} R_{args.fraction}={lagrange_r} pc{Style.RESET_ALL}"
            )
