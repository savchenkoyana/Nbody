"""Animated visualization of snapshot evolution."""

import argparse
import os
from functools import partial
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from utils.plot import create_animation
from utils.snap import get_timestamps
from utils.snap import parse_nemo

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
        "--n-timestamps",
        type=int,
        default=100,
        help="The number of timestamps to use for animation. Default: 100",
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
        "--add-mw-potential",
        action="store_true",
        help="Whether to add Milky Way potential (file with potential should be stored at "
        " 'Nbody/Agama/py/MWPotentialHunter24_rotating.ini')",
    )
    args = parser.parse_args()

    # Sanity checks
    if not os.path.exists(args.nemo_file):
        raise RuntimeError(f"{args.nemo_file} does not exist")
    if args.add_mw_potential:
        pot_path = "../Agama/py/MWPotentialHunter24_rotating.ini"
        if not os.path.exists(pot_path):
            raise RuntimeError(f"{pot_path} does not exist")
    if args.add_point_source and args.add_mw_potential:
        raise RuntimeError(
            "Cannot use '--add-point-source' and '--add-mw-potential' together. Choose one depending on how you performed evolution."
        )

    # Get timestamps for animation
    times = get_timestamps(
        filename=args.nemo_file,
        n_timestamps=args.n_timestamps,
    )

    # Initialize plot and simulation parameters
    fig = plt.figure(figsize=(10, 10), dpi=75)
    ax = plt.axes([0.08, 0.08, 0.9, 0.9])

    data = []

    center_x = np.array([], dtype=np.float32)
    center_y = np.array([], dtype=np.float32)

    for t in times:
        snap = parse_nemo(
            filename=args.nemo_file, t=t, remove_artifacts=not args.store_artifacts
        )  # mass, pos, vel

        x = snap[1]
        y = snap[2]
        label = f"Time={t}"

        data.append((x, y, label))

        m = snap[0]
        m_tot = np.sum(m)
        center_x = np.append(center_x, np.sum(m * x) / m_tot)
        center_y = np.append(center_y, np.sum(m * y) / m_tot)

    # Create custom function for updating animation
    def custom_update(
        i: int,
        data: list,
        ax: plt.axes,
        xlim: tuple[float, float],
        ylim: tuple[float, float],
        center_x: Optional[np.ndarray[np.float32]] = None,
        center_y: Optional[np.ndarray[np.float32]] = None,
    ):
        (
            x,
            y,
            label,
        ) = data[i]

        ax.cla()
        ax.set(xlim=xlim, ylim=ylim)

        ax.scatter(x, y, c="b", s=2, linewidths=0, label="Cluster bodies")

        if args.add_point_source:
            ax.scatter(0, 0, c="r", s=10, linewidths=0, label="SMBH")
        if args.add_mw_potential:
            pass  # TODO: implement

        ax.scatter(
            center_x[i],
            center_y[i],
            c="k",
            marker="v",
            s=10,
            linewidths=0,
            label="Cluster center-of-mass",
        )
        ax.legend(title=label if label else None, loc=1)  # upper right location

    update_animation = partial(
        custom_update,
        data=data,
        ax=ax,
        xlim=(-40000, 40000),
        ylim=(-40000, 40000),
        center_x=center_x,
        center_y=center_y,
    )

    ani = create_animation(
        data,
        ax=ax,
        fig=fig,
        n_frames=len(times),
        update_animation=update_animation,
    )
    ani.save("sim.gif", writer="pillow")
    plt.show()
