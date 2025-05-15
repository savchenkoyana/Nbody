"""This program plots average mass and Nparticles for given snapshots."""

from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_label
from utils.snap import get_timestamps

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots average mass and Nparticles for given snapshots."
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
        "--timeUnitMyr",
        nargs="+",
        type=float,
        default=[0.97779],
        help="Time unit in Myr. Default: 0.97779",
    )
    args = parser.parse_args()

    check_parameters(args)  # sanity checks
    if args.n_timestamps <= 0:
        raise RuntimeError("Got negative '--n-timestamps'")

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

    fig_nt, ax_nt = plt.subplots()  # N particles vs Time
    ax_nt.set_xlabel("$t$, Gyr")
    ax_nt.set_ylabel("$N(t) / N(t=0)$")
    ax_nt.set_ylim([0, 1])
    ax_nt.grid()
    ax_nt.set_title("Number of particles in cluster")

    fig_mt, ax_mt = plt.subplots()  # Mass vs Time
    ax_mt.set_xlabel("$t$, Gyr")
    ax_mt.set_ylabel(r"$M(t)$, $M_\odot$")
    ax_mt.grid()
    ax_mt.set_title("Mean mass of particles in cluster")

    for i, filename in enumerate(args.nemo_files):
        if not Path(filename).exists():
            raise RuntimeError(f"filename {filename} does not exist")

        times = np.array([], dtype=np.float32)
        n_particles = np.array([], dtype=np.float32)
        mean_mass = np.array([], dtype=np.float32)

        times_list = get_timestamps(
            filename=filename,
            n_timestamps=args.n_timestamps,
        )

        for snap in agama.NemoFile(filename):
            t = snap["Time"]
            if t in times_list:
                masses = snap["Mass"]

                times = np.append(times, t * 1e-3 * args.timeUnitMyr[i])
                n_particles = np.append(n_particles, masses.size)
                mean_mass = np.append(mean_mass, np.mean(masses))

        plot_label = (
            filename if len(args.nemo_files) > 1 else None
        )  # label as filename if there are many files
        # plot_label = (
        #     create_file_label(filename) if len(args.nemo_files) > 1 else None
        # )  # label as filename if there are many files

        fmt = "."
        ax_nt.plot(times, n_particles / n_particles[0], fmt, label=plot_label)
        ax_mt.plot(times, mean_mass, fmt, label=plot_label)

    ax_nt.legend(title=label)
    ax_mt.legend(title=label)

    fig_nt.savefig(save_dir / "N_cluster.png")
    fig_mt.savefig(save_dir / "M_cluster.png")

    plt.show()
