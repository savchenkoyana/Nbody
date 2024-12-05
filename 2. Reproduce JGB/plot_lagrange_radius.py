"""Plot lagrange radius for a given NEMO snapshot."""

from pathlib import Path

import matplotlib.pyplot as plt
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_label
from utils.snap import lagrange_radius_by_snap

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

    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    for t in args.times:
        snap_t, lagrange_r = lagrange_radius_by_snap(filename, t)
        plt.plot(snap_t, lagrange_r, "b.")

    plt.xlabel("$t$, 0.978 Gyr")
    plt.ylabel("Lagrange radius, $pc$")
    plt.legend(title=label)
    plt.title("Lagrange radii for 50% of mass")
    plt.show()
