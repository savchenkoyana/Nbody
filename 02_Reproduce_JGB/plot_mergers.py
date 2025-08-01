import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from utils.hdf5file import NBodySnapshot

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
    args = parser.parse_args()

    fig, ax = plt.subplots()  # N mergers
    ax.set_xlabel("$N$")
    ax.set_ylabel("$N_{mergers}$")
    ax.set_title("The number of mergers")

    fig_m, ax_m = plt.subplots()  # Mass distribution for mergers
    ax_m.set_xlabel(r"$M_1, M_{\odot}$")
    ax_m.set_ylabel(r"$M_2, M_{\odot}$")
    ax_m.set_xlim([0, 70])
    ax_m.set_ylim([0, 70])
    ax_m.set_title("Mass distribution for mergers")

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

        # Plot mass distribution
        df_m = pd.read_csv(exp / "coll.13", sep=r"\s+", skiprows=[0, 1])
        print(df_m[["M(I1)[M*]", "M(I2)[M*]"]])
        ax_m.scatter(df_m["M(I1)[M*]"], df_m["M(I2)[M*]"], marker=".", alpha=0.7)

        ax_m.plot([0, 70], [0, 70], "--", alpha=0.7, label="q=1")
        ax_m.plot([0, 70], [0, 35], "--", alpha=0.7, label="q=1/2")
        ax_m.plot([0, 70], [0, 17.5], "--", alpha=0.7, label="q=1/4")

        # Plot spin distribution

        for i in range(len(df_m)):
            df_m_i = df_m.iloc[i]

            t = df_m_i["TIME[NB]"]
            filename = exp / f"snap.40_{int(t + 0.5) + 1}.h5part"  # the next snapshot

            snap = NBodySnapshot(filename)
            it = iter(snap)
            snap = next(it)

            # More massive particle absorbs another during collision
            m1, m2 = df_m_i["M(I1)[M*]"], df_m_i["M(I2)[M*]"]
            ind = df_m_i["NAME(I1)"] if m1 > m2 else df_m_i["NAME(I2)"]
            q = m2 / m1 if m1 > m2 else m1 / m2

            def get_spin(snap, idx):
                if idx in snap.Name:
                    print(
                        f"Found particle {idx} in singles. M={snap.M[snap.Name == idx]}"
                    )
                    return snap.ASPN[snap.Name == idx]

                if getattr(snap, "Bin Name1", None) is not None:
                    name1 = getattr(snap, "Bin Name1")
                    if idx in name1:
                        print(
                            f"Found particle {idx} in binaries. M={getattr(snap, 'Bin M1*')[name1 == idx]}"
                        )
                        return snap.ASPN1[name1 == idx]

                    name2 = getattr(snap, "Bin Name2")
                    if idx in name2:
                        print(
                            f"Found particle {idx} in binaries. M={getattr(snap, 'Bin M2*')[name2 == idx]}"
                        )
                        return snap.ASPN2[name2 == idx]
                raise NotImplementedError(f"Merger case not implemented!")

            ax_s.scatter(q, get_spin(snap, ind))

    ax_m.legend()
    plt.show()
