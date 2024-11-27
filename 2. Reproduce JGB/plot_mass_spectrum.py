"""Plot mass spectrum for a given NEMO snapshot."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.general import mass_pdf
from utils.snap import parse_nemo

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
        masses = parse_nemo(filename=filename, t=t)[0]

        (counts, bins) = np.histogram(masses, bins=r, density=True)
        plt.hist(bins[:-1], bins, weights=counts, label=f"prof_{t}", histtype="step")

    plt.xscale("log")
    plt.legend()
    plt.show()
