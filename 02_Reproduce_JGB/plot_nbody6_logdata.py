import argparse
from pathlib import Path

import pandas as pd
from utils.nbody6_log import _ADJUST_DATA
from utils.nbody6_log import _COLS
from utils.nbody6_log import _OUTPUT_DATA
from utils.nbody6_log import load_scaling
from utils.nbody6_log import parse_adjust_data
from utils.nbody6_log import parse_output_data
from utils.nbody6_log import plot_adjust_data
from utils.nbody6_log import plot_output_data


def setup_pandas():
    """Setup pandas to display a full dataframe."""
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 2000)
    pd.set_option("display.float_format", "{:20,.2f}".format)
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
        setup_pandas()

    df = parse_adjust_data(args.log_file)
    data = parse_output_data(args.log_file)
    scalings = load_scaling(args.log_file)
    print(
        f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
    )

    # save data
    df.to_csv(save_dir / "adjust_data.csv", index=False)
    for key in data:
        data[key].to_csv(save_dir / f"{key}.csv", index=False)

    data = {**data, **scalings}

    # Plot and print selected data
    if values_adjust:
        plot_adjust_data(df, values_adjust, logscale=args.logscale)
        print(df[values_adjust])

    if values_output:
        plot_output_data(data, values_output, args.astro_units)
        for value in values_output:
            print("=" * 15, value, "=" * 15)
            print(data[value][_COLS])
