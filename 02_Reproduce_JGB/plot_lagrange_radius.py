"""Plot lagrange radius for a given NEMO snapshot."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_file_label
from utils.plot import create_label
from utils.snap import masses_in_lagrange_radius

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
        "--nbody-nemo-files",
        nargs="+",
        type=str,
        required=False,
        help="Same as '--nemo-files', but for NbodyX integrator output",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        type=float,
        required=True,
        help="Which times to use. Example: '--times 0.0 0.5 1.0'",
    )
    parser.add_argument(
        "--nbody-times",
        nargs="+",
        type=float,
        required=False,
        help="Same as '--times', but for NbodyX integrator output",
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

    agama.setUnits(length=1, mass=1, velocity=1)  # time units used for evolution
    timeUnitGyr = agama.getUnits()["time"] / 1e3  # time unit is 1 kpc / (1 km/s)

    # assuming filenames are like /path/to/Nbody/2.\ Reproduce\ JGB/<DIRNAME>/out.nemo
    save_dir = Path(args.nemo_files[0]).parents[1]

    fig_rt, ax_rt = plt.subplots()  # for Lagrange radius vs Time
    ax_rt.set_xlabel("$t$, Gyr")
    ax_rt.set_ylabel("Lagrange radius, $pc$")
    ax_rt.set_title("Lagrange radii for 50% of mass")

    fig_nt, ax_nt = plt.subplots()  # for N particles in Lagrange radius vs Time
    ax_nt.set_xlabel("$t$, Gyr")
    ax_nt.set_ylabel("$N(t) / N(t=0)$")
    ax_nt.set_title("Number of particles in cluster")

    fig_mt, ax_mt = plt.subplots()  # for Mass in Lagrange radius vs Time
    ax_mt.set_xlabel("$t$, Gyr")
    ax_mt.set_ylabel(r"$M(t)$, $M_\odot$")
    ax_mt.set_title("Mean mass of particles in cluster")

    if args.nbody_nemo_files is None:
        args.nbody_nemo_files = []

    args.nemo_files += args.nbody_nemo_files

    for filename in args.nemo_files:
        filename = Path(filename)
        if not filename.exists():
            raise RuntimeError(f"filename {filename} does not exist")

        times = np.array([], dtype=np.float32)
        lagrange_radii = np.array([], dtype=np.float32)
        n_particles = np.array([], dtype=np.float32)
        mean_mass = np.array([], dtype=np.float32)

        nbody_algo = (
            str(filename) in args.nbody_nemo_files
        )  # whether NEMO file is produced with NbodyX algo
        times_list = args.nbody_times if nbody_algo else args.times

        for t in times_list:
            try:
                masses, lagrange_r, mask = masses_in_lagrange_radius(
                    filename=filename,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                )
            except RuntimeError:
                if args.remove_outliers:
                    continue
                raise

            m_tot = np.sum(masses)
            m_filtered = masses[mask]

            times = np.append(times, t * timeUnitGyr)
            lagrange_radii = np.append(lagrange_radii, lagrange_r)
            n_particles = np.append(n_particles, m_filtered.size)
            mean_mass = np.append(mean_mass, np.mean(m_filtered))

        plot_label = (
            create_file_label(filename) if len(args.nemo_files) > 1 else None
        )  # label as filename if there are many files
        fmt = "v" if nbody_algo else "."
        ax_rt.plot(times, lagrange_radii, fmt, label=plot_label)
        ax_nt.plot(times, n_particles / n_particles[0], fmt, label=plot_label)
        ax_mt.plot(times, mean_mass, fmt, label=plot_label)

    # If legends are created before calling of ax.plot, there will be no labels
    ax_rt.legend(title=label)
    ax_nt.legend(title=label)
    ax_mt.legend(title=label)

    fig_rt.savefig(save_dir / "lagrange_radii.png")
    fig_nt.savefig(save_dir / "N_lagrange_radii.png")
    fig_mt.savefig(save_dir / "M_lagrange_radii.png")

    plt.show()
