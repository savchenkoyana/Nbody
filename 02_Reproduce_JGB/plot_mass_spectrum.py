"""Plot mass spectrum for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.general import mass_pdf
from utils.plot import create_label
from utils.snap import masses_in_lagrange_radius
from utils.snap import parse_nemo

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots mass spectrum for a given snapshot"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file used for mass spectrum computation",
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
    parser.add_argument(
        "--lagrange",
        action="store_true",
        help="Whether to plot only masses into the lagrange radius from density center (will be computed)",
    )
    args = parser.parse_args()

    check_parameters(args)  # sanity checks

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")
    save_dir = filename.absolute().parent

    # Plot original spectrum
    m = np.logspace(-2, 2)
    plt.plot(
        m,
        mass_pdf(m, mu=args.mu, scale=args.scale, sigma=args.sigma),
        linestyle="dotted",
        label="orig pdf",
    )

    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    agama.setUnits(length=1, mass=1, velocity=1)  # time units used for evolution
    timeUnitGyr = agama.getUnits()["time"] / 1e3  # time unit is 1 kpc / (1 km/s)

    for t in args.times:
        if args.lagrange:
            try:
                masses, lagrange_r, mask = masses_in_lagrange_radius(
                    filename=filename,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                )
                masses = masses[mask]
            except RuntimeError:
                if args.remove_outliers:
                    continue
                raise
        else:
            snap = parse_nemo(filename=filename, t=t)  # m, x, y, z, vx, vy, vz
            masses = snap[0]

        (counts, bins) = np.histogram(masses, bins=m, density=True)
        plt.hist(
            bins[:-1],
            bins,
            weights=counts,
            label=f"$t$={t * timeUnitGyr:.2f}",
            histtype="step",
        )

    plt.xscale("log")
    plt.xlabel(r"$M, M_\odot$")
    plt.legend(title=label)
    plt.title("Mass distribution in cluster")
    plt.savefig(save_dir / "mass_spectrum.png")
    plt.show()
