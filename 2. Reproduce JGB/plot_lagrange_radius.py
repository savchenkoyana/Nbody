"""Plot lagrange radius for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_label
from utils.snap import lagrange_radius_by_snap

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots mass spectrum for a given snapshot"
    )
    parser.add_argument(
        "--nemo-files",
        nargs="+",
        type=str,
        required=True,
        help="Nemo files used for lagrange radii computation",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        type=float,
        required=True,
        help="Which times to use. Example: '--times 0.0 0.5 1.0'",
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

    check_parameters(args)  # sanity checks
    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    agama.setUnits(length=1, mass=1, velocity=1)
    timeUnitGyr = agama.getUnits()["time"] / 1e3  # time unit is 1 kpc / (1 km/s)

    # assuming filenames are like /path/to/Nbody/2.\ Reproduce\ JGB/<DIRNAME>/out.nemo
    save_dir = Path(args.nemo_files[0]).parents[1]

    for filename in args.nemo_files:
        filename = Path(filename)
        if not filename.exists():
            raise RuntimeError(f"filename {filename} does not exist")

        x = np.array([], dtype=np.float32)
        y = np.array([], dtype=np.float32)

        for t in args.times:
            snap_t, lagrange_r = lagrange_radius_by_snap(
                filename, t, remove_artifacts=not args.store_artifacts
            )
            x = np.append(x, snap_t * timeUnitGyr)
            y = np.append(y, lagrange_r)

        if args.remove_outliers:
            # Check if there are outliers
            has_outliers = np.max(y) / np.min(y) > 500
            if has_outliers:
                print(
                    f"There are outliers as max={np.max(y)} and min={np.min(y)}! Filtering..."
                )
                mask = y < np.mean(y)
                x, y = x[mask], y[mask]

        plot_label = filename.parts[-2] if len(args.nemo_files) > 1 else None
        print("first Lagrange radius", x[0], y[0])
        plt.plot(x, y, ".", label=plot_label)

    plt.xlabel("$t$, Gyr")
    plt.ylabel("Lagrange radius, $pc$")
    plt.legend(title=label)
    plt.title("Lagrange radii for 50% of mass")
    plt.savefig(save_dir / "lagrange_radii.png")
    plt.show()
