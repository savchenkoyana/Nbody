"""Animated visualization of snapshot evolution."""

import argparse
import os
import subprocess
from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from tqdm.notebook import tqdm
from utils.plot import create_animation
from utils.snap import RemoveFileOnEnterExit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a movie with snapshot evolution"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file used for animation",
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
        "--add-point-source",
        action="store_true",
        help="Whether to add steady point source of gravity at the center of coordinates",
    )
    parser.add_argument(
        "--add-potential",
        action="store_true",
        help="Whether to add Milky Way potential (file with potential should be stored at "
        " 'Nbody/Agama/py/MWPotentialHunter24_rotating.ini')",
    )
    args = parser.parse_args()

    # Sanity checks
    if not os.path.exists(args.nemo_file):
        raise RuntimeError(f"{args.nemo_file} does not exist")
    if args.add_potential:
        pot_path = "../Agama/py/MWPotentialHunter24_rotating.ini"
        if not os.path.exists(pot_path):
            raise RuntimeError(f"{pot_path} does not exist")
    if args.add_point_source and args.add_potential:
        raise RuntimeError(
            "Cannot use '--add-point-source' and '--add-potential' together. Choose one depending on how you performed evolution."
        )

    # Initialize plot and simulation parameters
    fig = plt.figure(figsize=(10, 10), dpi=75)
    ax = plt.axes([0.08, 0.08, 0.9, 0.9])

    data = []

    for time in tqdm(args.times):
        snapfile = args.nemo_file.replace(".nemo", f"_{time}")

        with RemoveFileOnEnterExit(snapfile):
            subprocess.check_call(
                f"s2a {args.nemo_file} {snapfile} times={time}", shell=True
            )
            snap = np.loadtxt(snapfile).T  # mass, pos, vel

        x = snap[1, :]
        y = snap[2, :]
        label = f"Time={time}"

        data.append((x, y, label))

    # Create custom function for updating animation
    def custom_update(
        i: int,
        data: list,
        ax: plt.axes,
        xlim: tuple[float, float],
        ylim: tuple[float, float],
    ):
        (
            x,
            y,
            label,
        ) = data[i]

        ax.cla()
        ax.set(xlim=xlim, ylim=ylim)

        ax.scatter(x, y, c="b", s=2, linewidths=0)

        if args.add_point_source:
            ax.scatter(0, 0, c="r", s=10, linewidths=0)
        if args.add_potential:
            pass  # TODO: implement

        if label:
            ax.text(
                x=0.01,
                y=0.99,
                s=label,
                ha="left",
                va="top",
                transform=ax.transAxes,
            )

    update_animation = partial(
        custom_update,
        data=data,
        ax=ax,
        xlim=(-40, 40),
        ylim=(-40, 40),
    )

    ani = create_animation(
        data,
        ax=ax,
        fig=fig,
        n_frames=len(args.times),
        update_animation=update_animation,
    )
    plt.show()
