"""Plot density for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from postprocess_snap import postprocess
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
        "--proj-density",
        action="store_true",
        help="If '--proj-density' is given, the script calculates the density "
        "projected on a line of sight (see NEMO's 'projprof'). If False, the script "
        "calculates spherically symmetric density using NEMO's 'sphereprof'.",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        type=float,
        required=True,
        help="Which times to use. Example: '--times 0.0 0.5 1.0'",
    )
    parser.add_argument(
        "--postprocess",
        action="store_true",
        help="Whether to postprocess snapshot.",
    )
    parser.add_argument(
        "--remove-point-source",
        action="store_true",
        help="Whether to remove a steady point source of gravity at the center of coordinates.",
    )
    parser.add_argument(
        "--source-mass",
        type=float,
        default=4.37 * 10**10,
        help="Mass of point source of gravitational field (is solar masses). Default: 4.37x10^10",
    )
    args = parser.parse_args()

    check_parameters(args)  # sanity checks

    set_units()  # set Agama units

    filename = args.nemo_file
    if not Path(filename).exists():
        raise RuntimeError(f"filename {filename} does not exist")

    # Compute total mass for the distribution by multiplying the number of samples by E[x] of distribution
    mass_math_expectation = compute_mean_mass(
        mu=args.mu, scale=args.scale, sigma=args.sigma
    )
    m_tot = args.N * mass_math_expectation

    # Plot original density
    r = np.logspace(0, 2)
    xyz = np.vstack((r, r * 0, r * 0)).T

    potential = agama.Potential(
        type="Plummer",
        mass=m_tot,
        scaleRadius=args.plummer_r,
    )

    if args.proj_density:
        pass  # TODO: implement
    else:
        plt.plot(
            r, potential.density(xyz), linestyle="dotted", label="original density"
        )

    plt.xlabel("r")
    plt.ylabel(r"$\rho$")
    plt.xscale("log")
    plt.yscale("log")

    for t in args.times:
        proj_vector = None

        if args.postprocess:
            out_file = filename.replace(".nemo", "_postprocessed.nemo")

            _, xv_cm = postprocess(
                filename=filename,
                t=t,
                remove_point_source=args.remove_point_source,
                source_mass=args.source_mass,
                output_file=out_file,
            )
            proj_vector = xv_cm[:3] / np.sqrt(np.sum(xv_cm[:3] ** 2))  # normalized

        prof = profile_by_snap(
            filename=out_file if args.postprocess else filename,
            t=t,
            projvector=proj_vector if args.proj_density else None,
        )

        r_prof, rho_prof = prof[0], prof[1]

        plt.plot(r_prof, rho_prof, label=f"prof_{t}")

    plt.legend()
    plt.show()
