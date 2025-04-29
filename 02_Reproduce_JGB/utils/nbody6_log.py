"""Based on this jupyter-notebook: https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing/blob/stable/examples/01_Basics.ipynb"""
import re
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_OUTPUT_DATA = {"RLAGR", "AVMASS", "NPARTC", "SIGR2", "SIGT2", "VROT"}
_ADJUST_DATA = {
    "T[Myr]",
    "Q",
    "DE",
    "DELTA",
    "DETOT",
    "E",
    "EKIN",
    "POT",
    "ETIDE",
    "ETOT",
    "EBIN",
    "EMERGE",
    "ESUB",
    "ECOLL",
    "EMDOT",
    "ECDOT",
}

_FULL_COLS = [
    0.001,
    0.003,
    0.005,
    0.01,
    0.03,
    0.05,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    0.95,
    0.99,
    1.0,
    "<RC",
]
_COLS = [0.01, 0.1, 0.3, 0.5, 0.9, 1.0, "<RC"]

# ——— Data loading ———


def parse_adjust_data(logfile: str):
    """Parse lines produced at adjust stage."""
    df = None

    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            line = line.replace("*****", " nan")
            if re.search("ADJUST:", line):
                line = re.sub(r"\s+", " ", line).strip()
                line = line.split(" ")

                if df is None:
                    cols = [line[i] for i in range(3, len(line), 2)]
                    df = pd.DataFrame(columns=cols)

                idx = np.float64(line[2])
                df.loc[idx] = np.float64([line[i] for i in range(4, len(line), 2)])
    return df


def parse_output_data(logfile: str):
    """Parse lines produced at output stage."""
    data = {data_type: pd.DataFrame(columns=_FULL_COLS) for data_type in _OUTPUT_DATA}

    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            for data_type in _OUTPUT_DATA:
                if re.search(data_type, line):
                    line = re.sub(r"\s+", " ", line).strip()
                    line = line.split(" ")

                    (data[data_type]).loc[
                        np.float64(line[0].replace("D", "E"))
                    ] = np.float64(line[2:])
                    break

    return data


def load_scaling(logfile: str):
    """Get scale coefficient from log file."""
    pat = re.compile(
        r"""PHYSICAL\ SCALING:      # literal header
            \s*R\*\s*=\s*([0-9E+.\-]+)   # capture R*
            \s*M\*\s*=\s*([0-9E+.\-]+)   # capture M*
            \s*V\*\s*=\s*([0-9E+.\-]+)   # capture V*
            \s*T\*\s*=\s*([0-9E+.\-]+)   # capture T*
        """,
        re.VERBOSE,
    )

    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            m = re.search(pat, line)
            if m:
                keys = ["R*", "M*", "V*", "T*"]
                vals = map(float, m.groups())
                return dict(zip(keys, vals))


def load_data(dirname: Union[str, Path]):
    # load output data
    data = {name: pd.read_csv(Path(dirname) / f"{name}.csv") for name in _OUTPUT_DATA}
    # load adjust data
    df = pd.read_csv(Path(dirname) / "adjust_data.csv")
    return data, df


# ——— Data plotting ———


def plot_adjust_data(df: pd.DataFrame, plot_values: list, logscale: bool):
    """Plot data produced at 'adjust' stage.

    Y axis can be in default scale or logscale. Only N-body units are
    supported.
    """
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()

    df[plot_values].plot(ax=ax)

    ax.set_title(r"Energy evolution")
    ax.set_xlabel(r"Time t [nbody units]")
    ax.set_ylabel(r"Energy E [nbody units]")
    ax.grid()
    if logscale:
        ax.set_yscale("log")
    plt.show()
    return fig, ax


def plot_output_data(data: dict, plot_values: list, astro_units: bool):
    """Plot data produced at 'output' stage.

    Both N-body units and astro units are supported.
    """
    if astro_units:
        data["RLAGR"] *= data["R*"]
        data["AVMASS"] *= data["M*"]
        data["SIGR2"] *= data["V*"]
        data["SIGT2"] *= data["V*"]
        data["VROT"] *= data["V*"]

    N = len(plot_values)
    # choose columns close to square
    n_cols = np.ceil(np.sqrt(N)).astype(np.int32)
    n_rows = np.ceil(N / n_cols).astype(np.int32)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows))
    axes = np.atleast_1d(axes).flatten()

    for ax, pdata in zip(axes, plot_values):
        ax.set_title(f"{pdata} time evolution")
        for col in _COLS:
            y = data[pdata][col]
            x = np.arange(y.size)
            if astro_units:
                x = x * data["T*"]  # here we assume that deltat=1.0, TODO: rewrite
            ax.plot(x, y)

        if astro_units:
            ax.set_xlabel(r"Time t [Myr]")
            ax.set_ylabel(rf"{pdata} [astro units]")
        else:
            ax.set_xlabel(r"Time t [nbody units]")
            ax.set_ylabel(rf"{pdata} [nbody units]")

        ax.grid()

        if pdata != "VROT":
            ax.set_yscale("log")

    for ax in axes[N:]:
        ax.set_visible(False)

    fig.tight_layout()
    plt.show()
    return fig, ax
