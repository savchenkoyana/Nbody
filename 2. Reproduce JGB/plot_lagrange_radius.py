"""Plot lagrange radius for a given NEMO snapshot."""

from pathlib import Path

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
    args = parser.parse_args()

    check_parameters(args)  # sanity checks
    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

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
            x = np.append(x, snap_t)
            y = np.append(y, lagrange_r)

        print(x, y)
        plot_label = filename.stem if len(args.nemo_files) > 1 else None
        plt.plot(x, y, ".", label=plot_label)

    plt.xlabel("$t$, 0.978 Gyr")
    plt.ylabel("Lagrange radius, $pc$")
    plt.legend(title=label)
    plt.title("Lagrange radii for 50% of mass")
    plt.show()
