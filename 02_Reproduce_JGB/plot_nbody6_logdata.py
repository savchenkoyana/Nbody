import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from utils.nbody6_log import _ADJUST_DATA
from utils.nbody6_log import _COLS
from utils.nbody6_log import _HDF5_OUTPUT_DATA
from utils.nbody6_log import _OUTPUT_DATA
from utils.nbody6_log import load_data
from utils.nbody6_log import plot_adjust_data
from utils.nbody6_log import plot_hdf5_output_data
from utils.nbody6_log import plot_output_data


def setup_pandas():
    """Setup pandas to display a full dataframe."""
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 2000)
    pd.set_option("display.max_colwidth", None)


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
        help=f"Comma-separated column values to plot. Choose from {(*_OUTPUT_DATA, *_ADJUST_DATA)}",
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
    values_hdf5_output = list(values.intersection(_HDF5_OUTPUT_DATA))

    unknown_values = values.difference(_ADJUST_DATA, _OUTPUT_DATA, _HDF5_OUTPUT_DATA)
    if unknown_values:
        raise ValueError(f"Unknown columns {unknown_values}")

    if args.full_output:
        setup_pandas()

    data = load_data(args.log_file)
    adjust_data = data["adjust"]
    output_data = data["output"]
    hdf5_data = data["hdf5_output"]

    # save data
    adjust_data.to_csv(save_dir / "adjust_data.csv", index=False)
    for key in output_data:
        output_data[key].to_csv(save_dir / f"{key}.csv", index=False)

    if args.astro_units:
        scalings = data["scaling"]
        print(
            f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
        )
        output_data = {**output_data, **scalings}

    # Plot and print selected data
    if values_adjust:
        fix, ax = plot_adjust_data(adjust_data, values_adjust, logscale=args.logscale)
        plt.show()
        print(adjust_data[values_adjust])

    if values_output:
        fix, ax = plot_output_data(output_data, values_output, args.astro_units)
        plt.show()
        for value in values_output:
            print("=" * 15, value, "=" * 15)
            print(output_data[value][_COLS])

    if values_hdf5_output and not hdf5_data.empty:
        fix, ax = plot_hdf5_output_data(hdf5_data, values_hdf5_output)
        plt.show()
        for value in values_hdf5_output:
            print("=" * 15, value, "=" * 15)
            print(hdf5_data[value])
