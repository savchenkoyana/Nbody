import argparse
from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(file: str, key: int, color: tuple, linestyle: str, label: str):
    """Reads snapshots from the given file using Agama and extracts the
    trajectory for the specified particle key.

    Parameters:
        file (str): Path to the data file.
        key (int): The particle key to filter.
        color (tuple): Color for the trajectory plot.
        linestyle (str): Linestyle for the trajectory plot.
        label (str): Label for the plot legend.
    """
    positions = []

    for snap in agama.NemoFile(file):
        if "Key" not in snap:  # nbody0
            idx = key - 1
        else:
            indices = np.where(snap["Key"] == key)[0]
            if len(indices) != 1:
                raise RuntimeError(
                    f"Found {len(indices)} paricles with 'Key'={key} for {file} at 'Time'={snap['Time']}"
                )
            idx = indices[0]

        positions.append(snap["Position"][idx])

    positions = np.array(positions)
    plt.plot(
        positions[:, 0], positions[:, 1], color=color, linestyle=linestyle, label=label
    )


def main():
    parser = argparse.ArgumentParser(
        description="Plot particle trajectories using Agama NemoFile."
    )
    parser.add_argument(
        "--key", type=int, help="Particle key (integer) to filter trajectories."
    )
    parser.add_argument("--files", nargs="+", help="List of data files to process.")
    args = parser.parse_args()

    save_dir = Path(args.files[0]).parents[0]

    plt.figure(figsize=(8, 6))

    colors = plt.cm.tab10.colors  # 10 distinct colors
    linestyles = ["--", "-.", ":"]

    for i, file in enumerate(args.files):
        color = colors[i % len(colors)]
        linestyle = linestyles[i % len(linestyles)]
        plot_trajectory(file, args.key, color, linestyle, label=file)

    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title(f"Trajectories for Particle Key {args.key}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / f"traj_{args.key}.png")
    plt.show()


if __name__ == "__main__":
    main()
