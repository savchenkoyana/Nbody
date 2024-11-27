"""Plot density for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import compute_mean_mass
from utils.general import create_argparse
from utils.general import set_units
from utils.snap import profile_by_snap

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots density profile for a given snapshot"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file used for density profile computation",
    )
    parser.add_argument(
        "--proj-vector",
        type=float,
        nargs=3,
        default=[0, 0, 0],
        help="This vector is used for density profile calculations. "
        "If proj_vector contains only zeros, the script ignores it and calculates spherically symmetric density using NEMO's 'sphereprof'. "
        "Otherwise the script calculates projected density using the vector as a line of sight (see NEMO's 'projprof'). "
        "Default: [0, 0, 0]",
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

    set_units()  # set Agama units

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")
    save_dir = filename.absolute().parent

    # Compute total mass for the distribution by multiplying the number of samples by E[x] of distribution
    mass_math_expectation = compute_mean_mass(
        mu=args.mu, scale=args.scale, sigma=args.sigma
    )
    m_tot = args.N * mass_math_expectation

    # Compute proj_vector for plotting the density
    proj_vector = None if not np.any(args.proj_vector) else args.proj_vector

    # Plot original density
    r = np.logspace(0, 2)
    xyz = np.vstack((r, r * 0, r * 0)).T

    potential = agama.Potential(
        type="Plummer",
        mass=m_tot,
        scaleRadius=args.plummer_r,
    )

    if proj_vector is None:
        plt.plot(
            r, potential.density(xyz), linestyle="dotted", label="original density"
        )
    else:
        pass  # TODO: implement

    plt.xlabel("r")
    plt.ylabel(r"$\rho$")
    plt.xscale("log")
    plt.yscale("log")

    for t in args.times:
        prof = profile_by_snap(filename=filename, t=t, projvector=proj_vector)
        r_prof, rho_prof = prof[0], prof[1]

        plt.plot(r_prof, rho_prof, label=f"prof_{t}")

    plt.legend()
    plt.show()
