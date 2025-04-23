"""Based on this jupyter-notebook: https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing/blob/stable/examples/01_Basics.ipynb"""
import argparse
import re

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


# region Data Parsing


def parse_adjust_data(logfile: str):
    """Parse lines produced at adjust stage."""
    # initialize a pandas DataFrame
    df = None

    # work through the file
    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            # Match line where we get the mass fractions
            line = line.replace("*****", " nan")
            if re.search("ADJUST:", line):
                # Replace the multiple spaces by just one space
                line = re.sub(r"\s+", " ", line).strip()
                # After replacing the multiple spaces we can more easily split the line
                line = line.split(" ")

                # load dataframe
                if df is None:
                    cols = [line[i] for i in range(3, len(line), 2)]
                    df = pd.DataFrame(columns=cols)

                # Assign new row
                idx = np.float64(line[2])
                df.loc[idx] = np.float64([line[i] for i in range(4, len(line), 2)])
    return df


def parse_output_data(logfile: str):
    """Parse lines produced at output stage."""
    # set lines to analyze
    LINES_TO_READ = _OUTPUT_DATA

    # this time, just set the columns manually instead of letting
    # the program figure it out for itself.
    COLS = [
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

    # initialize dataframes to store results in
    data = {data_type: pd.DataFrame(columns=COLS) for data_type in LINES_TO_READ}

    # work through the file
    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            # work through all lines that should be read
            for data_type in LINES_TO_READ:
                # match lines with data type
                if re.search(data_type, line):
                    # prepare the line, for working with it
                    line = re.sub(r"\s+", " ", line).strip()
                    line = line.split(" ")

                    # We need to replace D by E, since python can not handle D as exponential,
                    # after that we set the row at time t by the following values
                    (data[data_type]).loc[
                        np.float64(line[0].replace("D", "E"))
                    ] = np.float64(line[2:])
                    # stop loop cause each line can only have one data type
                    break

    return data


# endregion


# region Plotting data


def plot_adjust_data(df, plot_values, logscale):
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()

    # plot
    df[plot_values].plot(ax=ax)

    # make the plot a little bit nicer
    ax.set_title(r"Energy evolution")
    ax.set_xlabel(r"Time t [nbody units]")
    ax.set_ylabel(r"Energy E [nbody units]")
    ax.grid()
    if logscale:
        ax.set_yscale("log")
    plt.show()
    return fig, ax


def plot_output_data(data, plot_values):
    # just plot the following fewer cols
    COLS = [0.1, 0.3, 0.5, 0.9, 1.0]

    # initialize matplotlib figure
    N = len(plot_values)
    # choose columns close to square
    n_cols = np.ceil(np.sqrt(N)).astype(np.int32)
    n_rows = np.ceil(N / n_cols).astype(np.int32)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows))
    axes = axes.flatten()

    for ax, pdata in zip(axes, plot_values):
        data[pdata][COLS].plot(ax=ax)

        ax.set_title(f"{pdata} time evolution")
        ax.set_xlabel(r"Time t [nbody units]")
        ax.set_ylabel(f"{pdata}")
        ax.grid()
        if pdata != "VROT":
            ax.set_yscale("log")

    for ax in axes[N:]:
        ax.set_visible(False)

    fig.tight_layout()
    plt.show()
    return fig, ax


# endregion


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Parses log file created by Nbody6++GPU-beijing and plots some stats."
    )
    parser.add_argument(
        "--log-file",
        type=str,
        required=True,
        help="Log file to parse",
    )
    parser.add_argument(
        "--values",
        type=str,
        help=f"Comma-separated column values to plot. Choose one of {(*_OUTPUT_DATA, *_ADJUST_DATA)}",
    )
    parser.add_argument(
        "--logscale",
        action="store_true",
        help="Whether to use logscale for Y axis for 'adjust' plots",
    )
    args = parser.parse_args()

    values = {x for x in args.values.split(",")}
    values_adjust = list(values.intersection(_ADJUST_DATA))
    values_output = list(values.intersection(_OUTPUT_DATA))

    unknow_values = values.difference(_ADJUST_DATA, _OUTPUT_DATA)
    if unknow_values:
        raise ValueError(f"Unknown columns {unknow_values}")

    # Plot
    if values_adjust:
        df = parse_adjust_data(args.log_file)
        plot_adjust_data(df, values_adjust, logscale=args.logscale)
        print(df[values_adjust])

    if values_output:
        data = parse_output_data(args.log_file)
        plot_output_data(data, values_output)
        print(data[values_output])
