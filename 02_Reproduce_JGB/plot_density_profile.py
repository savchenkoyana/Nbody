"""Plot density for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import compute_mean_mass
from utils.general import create_argparse
from utils.general import set_units
from utils.plot import create_label
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
        "--projprof",
        action="store_true",
        help="Whether to plot projected density profile ('projprof')."
        "By default plots spherical density profile 'sphereprof'.",
    )
    parser.add_argument(
        "--proj-vector",
        type=float,
        nargs=3,
        help="Vector for density profile calculations when using '--projprof'.",
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

    agama.setUnits(length=1, mass=1, velocity=1)  # time units used for evolution
    timeUnitGyr = agama.getUnits()["time"] / 1e3  # time unit is 1 kpc / (1 km/s)

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
    if args.projprof and args.proj_vector is None:
        raise RuntimeError("--proj-vector should be set when using --projprof!")
    proj_vector = args.proj_vector if args.projprof else None

    # Plot original density
    r = np.logspace(0, 2)
    xyz = np.vstack((r, r * 0, r * 0)).T

    potential = agama.Potential(
        type="Plummer",
        mass=m_tot,
        scaleRadius=args.plummer_r,
    )

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("$r, pc$")

    if args.projprof:
        plt.ylabel(r"$\rho, M_\odot / pc^2$")
    else:
        plt.plot(
            r, potential.density(xyz), linestyle="dotted", label=r"original $\rho(r)$"
        )
        plt.ylabel(r"$\rho, M_\odot / pc^3$")

    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    for t in args.times:
        prof = profile_by_snap(
            filename=filename,
            t=t,
            projvector=proj_vector,
            remove_artifacts=not args.store_artifacts,
        )
        try:
            r_prof, rho_prof = prof[0], prof[1]
        except IndexError:  # dens_centre failed to find a center
            if args.remove_outliers:
                continue
            raise

        plt.plot(r_prof, rho_prof, label=f"$t$={t * timeUnitGyr:.2f}")

    plt.legend(title=label)
    if args.projprof:
        plt.title("Projected density of the cluster")
    else:
        plt.title("Spherical density of the cluster")

    plt.savefig(save_dir / "density_profile.png")
    plt.show()
