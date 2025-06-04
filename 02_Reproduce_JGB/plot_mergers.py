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
        "--exps",
        type=str,
        nargs="+",
        required=True,
        help="Path to directory with event.35 file",
    )
    args = parser.parse_args()

    for exp in args.exps:
        exp = Path(exp)

        df = pd.read_csv(exp / "event.35", sep=r"\s+", skiprows=[0], header=None)
        df_col = pd.read_csv(exp / "event.35")
        colnames = list(df_col.columns)[0].split()
        colnames_last = colnames[-1]
        colnames = colnames[:-1] + [f"{colnames_last}_{i}" for i in range(16)]
        df.columns = colnames

        n_events = np.max(df["NCOLL"])
        n_particles = df.iloc[0]["NTYPE(1:16)_14"]

        if n_events:
            plt.bar(n_particles, n_events, bottom=[-0.01], width=100)
        else:
            plt.plot(n_particles, 0, marker="x", color="red")

        plt.xlabel("N")
        plt.ylabel("$N_{mergers}$")

    plt.show()
