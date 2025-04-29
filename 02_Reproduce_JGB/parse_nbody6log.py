"""Based on this jupyter-notebook: https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing/blob/stable/examples/01_Basics.ipynb"""
import argparse
import re
from pathlib import Path

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


def pandas_setup():
    """Setup pandas to display a full dataframe."""
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 2000)
    pd.set_option("display.float_format", "{:20,.2f}".format)
    pd.set_option("display.max_colwidth", None)


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

    # initialize dataframes to store results in
    data = {data_type: pd.DataFrame(columns=_FULL_COLS) for data_type in LINES_TO_READ}

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


def get_scaling(logfile: str):
    """Get scale coefficient from log file."""
    # compile one regex that matches the four starred quantities
    pat = re.compile(
        r"""PHYSICAL\ SCALING:      # literal header
            \s*R\*\s*=\s*([0-9E+.\-]+)   # capture R*
            \s*M\*\s*=\s*([0-9E+.\-]+)   # capture M*
            \s*V\*\s*=\s*([0-9E+.\-]+)   # capture V*
            \s*T\*\s*=\s*([0-9E+.\-]+)   # capture T*
        """,
        re.VERBOSE,
    )

    # work through the file
    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            m = re.search(pat, line)
            if m:
                # convert to float and store
                keys = ["R*", "M*", "V*", "T*"]
                vals = map(float, m.groups())
                results = dict(zip(keys, vals))
                return results


# endregion


# region Plotting data


def plot_adjust_data(df: pd.DataFrame, plot_values: list, logscale: bool):
    """Plot data produced at 'adjust' stage.

    Y axis can be in default scale or logscale. Only N-body units are
    supported.
    """
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

    # initialize matplotlib figure
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
                x = x * data["T*"]
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
    parser.add_argument(
        "--full-output",
        action="store_true",
        help="Whether to print rows/columns at full",
    )
    parser.add_argument(
        "--astro-units",
        action="store_true",
        help=f"Whether to plot values in astrophysical units (only for {_OUTPUT_DATA})",
    )
    args = parser.parse_args()
    save_dir = Path(args.log_file).parent

    values = {x for x in args.values.split(",")}
    values_adjust = list(values.intersection(_ADJUST_DATA))
    values_output = list(values.intersection(_OUTPUT_DATA))

    unknow_values = values.difference(_ADJUST_DATA, _OUTPUT_DATA)
    if unknow_values:
        raise ValueError(f"Unknown columns {unknow_values}")

    if args.full_output:
        pandas_setup()

    df = parse_adjust_data(args.log_file)
    data = parse_output_data(args.log_file)
    scalings = get_scaling(args.log_file)
    print(
        f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
    )

    # save data
    df.to_csv(save_dir / "adjust_data.csv", index=False)
    for key in data:
        data[key].to_csv(save_dir / f"{key}.csv", index=False)

    data = {**data, **scalings}

    # Plot
    if values_adjust:
        plot_adjust_data(df, values_adjust, logscale=args.logscale)
        print(df[values_adjust])

    if values_output:
        plot_output_data(data, values_output, args.astro_units)
        for value in values_output:
            print("=" * 15, value, "=" * 15)
            print(data[value][_COLS])
