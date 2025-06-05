import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

_EVENT_TYPE = yaml.safe_load(open("utils/nbody6_events.yaml"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Plots the number of mergers.")
    parser.add_argument(
        "--exp",
        type=str,
        nargs="+",
        required=True,
        help="Path to directory with event.35 file",
    )
    parser.add_argument(
        "--mass",
        action="store_true",
        help="Whether to plot mass distribution",
    )
    parser.add_argument(
        "--spin",
        action="store_true",
        help="Whether to plot spin distribution",
    )
    args = parser.parse_args()

    fig, ax = plt.subplots()  # N mergers
    ax.set_xlabel("$N$")
    ax.set_ylabel("$N_{mergers}$")
    ax.set_title("The number of mergers")

    if args.mass:
        fig_m, ax_m = plt.subplots()  # Mass distribution for mergers
        ax_m.set_xlabel(r"$M_1, M_{\odot}$")
        ax_m.set_ylabel(r"$M_2, M_{\odot}$")
        ax_m.set_xlim([0, 70])
        ax_m.set_ylim([0, 70])
        ax_m.set_title("Mass distribution for mergers")

    if args.spin:
        fig_s, ax_s = plt.subplots()  # Spin distribution for mergers
        ax_s.set_xlabel("Q")
        ax_s.set_ylabel("$a_f$")
        ax_s.set_title("Spin of mergers as a function of mass ratio")

    for exp in args.exp:
        exp = Path(exp)

        # Plot the number of mergers
        df = pd.read_csv(exp / "event.35", sep=r"\s+", skiprows=[0], header=None)
        df_col = pd.read_csv(exp / "event.35")
        colnames = list(df_col.columns)[0].split()
        colnames_last = colnames[-1]
        colnames = colnames[:-1] + [f"{colnames_last}_{i}" for i in range(16)]
        df.columns = colnames

        n_events = np.max(df["NCOLL"])
        n_particles = df.iloc[0]["NTYPE(1:16)_14"]

        if n_events:
            ax.bar(n_particles, n_events, bottom=[-0.01], width=100)
        else:
            ax.plot(n_particles, 0, marker="x", color="red")

        if args.mass:
            df = pd.read_csv(exp / "coll.13", sep=r"\s+", skiprows=[0, 1])
            ax_m.scatter(df["M(I1)[M*]"], df["M(I2)[M*]"], marker=".", alpha=0.7)

            ax_m.plot([0, 70], [0, 70], "--", alpha=0.7, label="q=1")
            ax_m.plot([0, 70], [0, 35], "--", alpha=0.7, label="q=1/2")
            ax_m.plot([0, 70], [0, 17.5], "--", alpha=0.7, label="q=1/4")
            ax_m.legend()

    plt.show()
