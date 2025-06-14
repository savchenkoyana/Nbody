"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from utils.snap import count_binaries
from utils.snap import get_momentum
from utils.snap import get_timestamps
from utils.snap import get_virial

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program prints statistics for a given NEMO snapshot"
    )
    parser.add_argument(
        "--nemo-files",
        nargs="+",
        type=str,
        required=True,
        help="Nemo files used for analysis",
    )
    parser.add_argument(
        "--n-timestamps",
        type=int,
        default=100,
        help="The number of timestamps to return. Default: 100",
    )
    parser.add_argument(
        "--eps",
        nargs="+",
        type=float,
        default=None,
        help="Gravitational softening. Required with '--virial' (used for softening) and '--binaries' (used to compute a threshold on distance)."
        " Note that we don't use --eps for softetning when counting binaries!",
    )
    parser.add_argument(
        "--virial",
        action="store_true",
        help="Whether to evaluate virial statistics",
    )
    parser.add_argument(
        "--momentum",
        action="store_true",
        help="Whether to evaluate momentum statistics",
    )
    parser.add_argument(
        "--binaries",
        action="store_true",
        help="Whether to plot the number of binaries. Warning: this option is slow, better use with '--n-timestamps 10'",
    )
    parser.add_argument(
        "--store-artifacts",
        action="store_true",
        help="Whether to store NEMO artifacts for debug",
    )
    args = parser.parse_args()

    # Sanity checks
    if args.n_timestamps <= 0:
        raise RuntimeError(
            f"--n-timestamps should be positive, got {args.n_timestamps}"
        )
    if args.virial or args.binaries:
        if not args.eps:
            raise RuntimeError(
                f"Gravitational softening eps should be set, got {args.eps}"
            )

        if len(args.eps) == 1:
            args.eps = args.eps * len(args.nemo_files)
        elif len(args.eps) != len(args.nemo_files):
            raise RuntimeError(
                f"--eps should have the same length as --nemo-files (or 1), got len={len(args.eps)}"
            )

    # assuming filenames are: /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/out.nemo
    # we will save data into /path/to/Nbody/02_Reproduce_JGB
    save_dir = Path(args.nemo_files[0]).parents[1]

    # Create subplots if needed
    if args.virial:
        fig_E, ax_E = plt.subplots()  # E vs Time
        ax_E.set_xlabel("$t$, Gyr")
        ax_E.set_ylabel("T+W")
        ax_E.set_title("Energy")

        fig_E2, ax_E2 = plt.subplots()  # E (relative) vs Time
        ax_E2.set_xlabel("$t$, Gyr")
        ax_E2.set_ylabel("$E/E(t=0)$")
        ax_E2.set_title("Energy (relative)")

        fig_vir, ax_vir = plt.subplots()  # Virial ratio vs Time
        ax_vir.set_xlabel("$t$, Gyr")
        ax_vir.set_ylabel("-2T/W")
        ax_vir.set_title("Virial ratio")

    if args.momentum:
        fig_Vcm, ax_Vcm = plt.subplots()  # Vcm vs Time
        ax_Vcm.set_xlabel("$t$, Gyr")
        ax_Vcm.set_ylabel("$V_{cm}$, km/s")
        ax_Vcm.set_title("Center-of-mass velocity")

        fig_Lz, ax_Lz = plt.subplots()  # Lz vs Time
        ax_Lz.set_xlabel("$t$, Gyr")
        ax_Lz.set_ylabel(r"$L_z$, 232533 x M_\odot x km/s x kpc")
        ax_Lz.set_title("Angular momentum (z-component)")

    if args.binaries:
        fig_binaries, ax_binaries = plt.subplots()  # Number of binaries vs Times
        ax_binaries.set_xlabel("$t$, Gyr")
        ax_binaries.set_ylabel("$N_{binaries}$")
        ax_binaries.set_title("Number of binaries")

    # Start task evaluation
    for i, filename in enumerate(args.nemo_files):
        if not Path(filename).exists():
            raise RuntimeError(f"filename {filename} does not exist")

        timestamps = get_timestamps(
            filename=filename,
            n_timestamps=args.n_timestamps,
        )
        print(f"\tTimestamps for\t{filename}\n", *timestamps)

        plot_label = (
            filename if len(args.nemo_files) > 1 else None
        )  # label as filename if there are many files
        # plot_label = (
        #     create_file_label(filename) if len(args.nemo_files) > 1 else None
        # )  # label as filename if there are many files

        if args.virial:
            virial_ratio, energy = [], []

            for t in timestamps:
                data = get_virial(
                    filename=filename,
                    eps=args.eps[i],
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                )  # time, 2T/W, T+W, T, W_acc, W_phi, W_exact, M
                virial_ratio.append(data[1])
                energy.append(data[2])

            ax_E.plot(timestamps, energy, ".", label=plot_label)
            ax_E2.plot(timestamps, energy / energy[0], ".", label=plot_label)
            ax_vir.plot(timestamps, virial_ratio, ".", label=plot_label)

        if args.momentum:
            velocity_cm, angular_momentum = [], []

            for t in timestamps:
                data = get_momentum(
                    filename=filename,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                )  # pos, x, y, z, vel, vx, vy, vz, l, lx, ly, lz

                velocity_cm.append(data[4])
                angular_momentum.append(data[-1])

            ax_Vcm.plot(timestamps, velocity_cm, ".", label=plot_label)
            ax_Lz.plot(timestamps, angular_momentum, ".", label=plot_label)

        if args.binaries:
            binaries = []

            for t in timestamps:
                count = count_binaries(filename=filename, t=t, r_threshold=args.eps[i])
                binaries.append(count)

            ax_binaries.plot(timestamps, binaries, ".", label=plot_label)

    if args.virial:
        ax_E.plot(
            timestamps, np.ones_like(timestamps) * energy[0], linestyle="--", label="IC"
        )
        ax_E2.plot(timestamps, np.ones_like(timestamps), linestyle="--", label="IC")
        ax_vir.plot(timestamps, np.ones_like(timestamps), linestyle="--", label="IC")

        ax_E.legend()
        ax_E2.legend()
        ax_vir.legend()

        fig_E.savefig(save_dir / "E.png")
        fig_E2.savefig(save_dir / "E_relative.png")
        fig_vir.savefig(save_dir / "vir.png")

    if args.momentum:
        ax_Vcm.plot(
            timestamps,
            np.ones_like(timestamps) * velocity_cm[0],
            linestyle="--",
            label="IC",
        )
        ax_Lz.plot(
            timestamps,
            np.ones_like(timestamps) * angular_momentum[0],
            linestyle="--",
            label="IC",
        )

        ax_Vcm.legend()
        ax_Lz.legend()

        fig_Vcm.savefig(save_dir / "Vcm.png")
        fig_Lz.savefig(save_dir / "Lz.png")

    if args.binaries:
        ax_binaries.legend()

        fig_binaries.savefig(save_dir / "binaries.png")

    if args.virial or args.momentum or args.binaries:
        plt.show()
