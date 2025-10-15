import argparse
from pathlib import Path
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from utils.nbody6_log import load_data
from utils.nbody6_log import plot_adjust_data

_EVENT_TYPE = yaml.safe_load(open("utils/nbody6_events.yaml"))


def plot_events_vline(
    events: dict,
    event_times: list,
    ax: Optional[matplotlib.axes._axes.Axes] = None,
):
    if ax is None:
        ax = plt.gca()

    for t in event_times:
        ax.axvline(t, linestyle="--", alpha=0.5, color="r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Parses event.35 data (KZ(19) or KZ(27) should be actuvated during simulation!)."
    )
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Path to directory with event.35 file",
    )
    args = parser.parse_args()
    exp = Path(args.exp)

    df = pd.read_csv(exp / "event.35", sep=r"\s+", skiprows=[0], header=None)
    df_col = pd.read_csv(exp / "event.35")
    colnames = list(df_col.columns)[0].split()
    colnames_last = colnames[-1]
    colnames = colnames[:-1] + [f"{colnames_last}_{i}" for i in range(16)]
    df.columns = colnames
    event_types = set(_EVENT_TYPE.keys()).intersection(df.columns)

    event_times = []
    events = {}

    # print events
    for column in event_types:
        event_counter = df[column].unique()
        print(f"{column}: {np.max(event_counter)} ({_EVENT_TYPE[column]})")
        if len(event_counter) > 1:
            for i in event_counter[1:]:
                event_time = df[df[column] == i].index[0]
                event_times.append(event_time)
                events.setdefault(event_time, []).append(column)

                print(f"\t Event {i} happened at T[NB]={event_time}")

    df_adjust = load_data(exp / "exp.out")["adjust"]

    # Get time [NB] of energy non-conservation
    df_adjust_large_de = df_adjust[np.abs(df_adjust["DE"]) > 1e-5]
    t_nb_large_de = df_adjust_large_de.index.values.astype(np.int32)

    event_times = set(event_times)
    t_nb_large_de = set(t_nb_large_de)
    event_times = event_times.intersection(t_nb_large_de)

    # plot DE
    fig_de = plt.figure(figsize=(9, 6))
    ax_de = fig_de.gca()
    ax_de.set_title(r"DE")
    ax_de.set_xlabel(r"Time t [nbody units]")
    ax_de.set_ylabel(r"DE [nbody units]")
    ax_de.grid()
    plt.plot(df_adjust["DE"])
    plot_events_vline(ax=ax_de, events=events, event_times=event_times)

    if event_times:
        text = (
            "DE>1e-5, got "
            + ", ".join(
                f"{df_adjust_large_de.at[t, 'DE']:.1e} (t={t:.2f})"
                for t in sorted(event_times)
            )
            + " (from event.35)"
        )
        plt.subplots_adjust(bottom=0.15)
        fig_de.text(0.5, 0.05, text, ha="center", fontsize=10)

    # plot DETOT
    fig_detot = plt.figure(figsize=(9, 6))
    ax_detot = fig_detot.gca()
    ax_detot.set_title(r"DETOT")
    ax_detot.set_xlabel(r"Time t [nbody units]")
    ax_detot.set_ylabel(r"DETOT [nbody units]")
    ax_detot.grid()
    plt.plot(df_adjust["DETOT"])
    plot_events_vline(ax=ax_detot, events=events, event_times=event_times)

    if event_times:
        text = (
            "DE>1e-5, got "
            + ", ".join(
                f"{df_adjust_large_de.at[t, 'DE']:.1e} (t={t:.2f})"
                for t in sorted(event_times)
            )
            + " (from event.35)"
        )
        plt.subplots_adjust(bottom=0.15)
        fig_detot.text(0.5, 0.05, text, ha="center", fontsize=10)

    # plot other distributions
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # plot EKIN, POT, ETIDE, ETOT
    plot_adjust_data(
        df_adjust, ["EKIN", "POT", "ETIDE", "ETOT", "Q"], logscale=False, ax=axes[0]
    )
    plot_events_vline(ax=axes[0], events=events, event_times=event_times)

    # plot EBIN, EMERGE, ESUB
    plot_adjust_data(df_adjust, ["EBIN", "EMERGE", "ESUB"], logscale=False, ax=axes[1])
    plot_events_vline(ax=axes[1], events=events, event_times=event_times)

    # plot ECOLL, EMDOT, ECDOT
    plot_adjust_data(df_adjust, ["ECOLL", "EMDOT", "ECDOT"], logscale=False, ax=axes[2])
    plot_events_vline(ax=axes[2], events=events, event_times=event_times)

    if event_times:
        text = (
            "DE>1e-5, got "
            + ", ".join(
                f"{', '.join(events[t])} (t={t:.2f})" for t in sorted(event_times)
            )
            + " (from event.35)"
        )
        plt.subplots_adjust(bottom=0.1)
        fig.text(0.5, 0.02, text, ha="center", fontsize=10)

    plt.show()
