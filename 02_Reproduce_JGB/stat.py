"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from utils.snap import get_timestamps
from utils.snap import get_virial_parameters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program prints statistics for a given NEMO snapshot"
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
        help="The number of timestamps to return. Default: 100",
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=None,
        help="Gravitational softening. Required if target is 'E' or '2T/W'",
    )
    parser.add_argument(
        "--virial",
        action="store_true",
        help="Whether to evaluate virial statistics",
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
    if args.virial and not args.eps:
        raise RuntimeError(f"Gravitational softening eps should be set, got {args.eps}")

    # assuming filenames are: /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/out.nemo
    # we will save data into /path/to/Nbody/02_Reproduce_JGB
    save_dir = Path(args.nemo_files[0]).parents[1]

    # Create subplots if needed
    if args.virial:
        fig_E, ax_E = plt.subplots()  # E vs Time
        ax_E.set_xlabel("$t$, Gyr")
        ax_E.set_ylabel("T+W")
        ax_E.set_title("Energy")

        fig_vir, ax_vir = plt.subplots()  # Mass in Lagrange radius vs Time
        ax_vir.set_xlabel("$t$, Gyr")
        ax_vir.set_ylabel("-2T/W")
        ax_vir.set_title("Virial ratio")

    # Start task evaluation
    for filename in args.nemo_files:
        if not Path(filename).exists():
            raise RuntimeError(f"filename {filename} does not exist")

        timestamps = get_timestamps(
            filename=filename,
            n_timestamps=args.n_timestamps,
        )
        print(f"\tTimestamps for\t{filename}\n", *timestamps)

        if args.virial:
            virial_ratio, energy = [], []

            for t in timestamps:
                data = get_virial_parameters(
                    filename=filename,
                    eps=args.eps,
                    t=t,
                    remove_artifacts=not args.store_artifacts,
                )  # time, 2T/W, T+W, T, W_acc, W_phi, W_exact, M
                virial_ratio.append(data[1])
                energy.append(data[2])

            plot_label = (
                filename.split("/")[-1] if len(args.nemo_files) > 1 else None
            )  # label as filename if there are many files
            # plot_label = (
            #     create_file_label(filename) if len(args.nemo_files) > 1 else None
            # )  # label as filename if there are many files

            ax_E.plot(timestamps, energy, ".", label=plot_label)
            ax_vir.plot(timestamps, virial_ratio, ".", label=plot_label)

    if args.virial:
        ax_E.plot(
            timestamps, np.ones_like(timestamps) * energy[0], linestyle="--", label="IC"
        )
        ax_vir.plot(timestamps, np.ones_like(timestamps), linestyle="--", label="IC")

        ax_E.legend()
        ax_vir.legend()

        fig_E.savefig(save_dir / "E.png")
        fig_vir.savefig(save_dir / "vir.png")

        plt.show()
