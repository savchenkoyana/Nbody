"""This program plots lagrange radius and other related stats for given
snapshots."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_label
from utils.snap import get_timestamps
from utils.snap import masses_in_lagrange_radius

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots lagrange radius and other related stats for given snapshots"
    )
    parser.add_argument(
        "--nemo-files",
        nargs="+",
        type=str,
        required=True,
        help="Nemo files used for lagrange radii computation",
    )
    parser.add_argument(
        "--n-timestamps",
        type=int,
        default=100,
        help="The number of timestamps to use for plot. Default: 100",
    )
    parser.add_argument(
        "--dens-parameter",
        type=int,
        default=500,
        help="The number of neighbours in SPH-like estimation for 'dens_centre' manipulator. If 0, density center is not computed. Default: 500",
    )
    parser.add_argument(
        "--timeUnitMyr",
        nargs="+",
        type=float,
        default=[0.97779],
        help="Time unit in Myr. Default: 0.97779",
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
    if args.n_timestamps <= 0:
        raise RuntimeError("Got negative '--n-timestamps'")
    if args.dens_parameter < 0:
        raise RuntimeError("Got negative '--dens-parameter'")

    if len(args.timeUnitMyr) == 1:
        args.timeUnitMyr = args.timeUnitMyr * len(args.nemo_files)
    elif len(args.timeUnitMyr) != len(args.nemo_files):
        raise RuntimeError(
            f"--timeUnitMyr should have the same length as --nemo-files (or 1), got len={len(args.timeUnitMyr)}"
        )

    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    # assuming filenames are: /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/out.nemo
    # we will save data into /path/to/Nbody/02_Reproduce_JGB
    save_dir = Path(args.nemo_files[0]).parents[1]

    fig_rt, ax_rt = plt.subplots()  # Lagrange radius vs Time
    ax_rt.set_xlabel("$t$, Gyr")
    ax_rt.set_ylabel("Lagrange radius, $pc$")
    ax_rt.set_title("Lagrange radii for 50% of mass")

    fig_nt, ax_nt = plt.subplots()  # N particles in Lagrange radius vs Time
    ax_nt.set_xlabel("$t$, Gyr")
    ax_nt.set_ylabel("$N(t) / N(t=0)$")
    ax_nt.set_ylim([0, 1])
    ax_nt.set_title("Number of particles in cluster")

    fig_mt, ax_mt = plt.subplots()  # Mass in Lagrange radius vs Time
    ax_mt.set_xlabel("$t$, Gyr")
    ax_mt.set_ylabel(r"$M(t)$, $M_\odot$")
    ax_mt.set_title("Mean mass of particles in cluster")

    for i, filename in enumerate(args.nemo_files):
        if not Path(filename).exists():
            raise RuntimeError(f"filename {filename} does not exist")

        times = np.array([], dtype=np.float32)
        lagrange_radii = np.array([], dtype=np.float32)
        n_particles = np.array([], dtype=np.float32)
        mean_mass = np.array([], dtype=np.float32)

        times_list = get_timestamps(
            filename=filename,
            n_timestamps=args.n_timestamps,
        )

        for t in times_list:
            try:
                masses, lagrange_r, mask = masses_in_lagrange_radius(
                    filename=filename,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                    dens_par=args.dens_parameter,
                )
            except RuntimeError:
                if args.remove_outliers:
                    continue
                raise

            m_tot = np.sum(masses)
            m_filtered = masses[mask]

            times = np.append(times, t * 1e-3 * args.timeUnitMyr[i])
            lagrange_radii = np.append(lagrange_radii, lagrange_r)
            n_particles = np.append(n_particles, m_filtered.size)
            mean_mass = np.append(mean_mass, np.mean(m_filtered))

        plot_label = (
            filename if len(args.nemo_files) > 1 else None
        )  # label as filename if there are many files
        # plot_label = (
        #     create_file_label(filename) if len(args.nemo_files) > 1 else None
        # )  # label as filename if there are many files

        fmt = "."
        ax_rt.plot(times, lagrange_radii, fmt, label=plot_label)
        ax_nt.plot(times, n_particles / n_particles[0], fmt, label=plot_label)
        ax_mt.plot(times, mean_mass, fmt, label=plot_label)

    ax_rt.legend(title=label)
    ax_nt.legend(title=label)
    ax_mt.legend(title=label)

    fig_rt.savefig(save_dir / "lagrange_radii.png")
    fig_nt.savefig(save_dir / "N_lagrange_radii.png")
    fig_mt.savefig(save_dir / "M_lagrange_radii.png")

    plt.show()
