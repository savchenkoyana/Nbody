"""Parses NbodyX input to give human-readable summary."""

import argparse

from utils.nbody_input import kz as kz_mapping
from utils.nbody_input import parameters as parameter_mapping
from utils.nbody_input import parse_input_file


def print_results(data, version):
    print("Non-zero KZ parameters:")
    kz_dict = kz_mapping.get(version, {})
    for i, value in enumerate(data["KZ"], start=1):
        if value != 0:
            meaning = kz_dict.get(i, "Unknown KZ option")
            print(f"  KZ{i}: {value} ({meaning})")

    print("\nOther parameters:")
    # For each parameter (except KZ), print the value along with its description.
    parameter_dict = parameter_mapping.get(version, {})
    for key, value in data.items():
        if key == "KZ":
            continue
        desc = parameter_dict.get(key, "No description available.")
        print(f"  {key}: {value} -- {desc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse an input file or a user-supplied KZ line and extract relevant parameters."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--filename", "-f", type=str, help="Path to the input file")
    group.add_argument(
        "--kz",
        type=str,
        help="Comma-separated KZ values to parse instead of reading from file",
    )
    parser.add_argument(
        "--version",
        type=str,
        choices=["nbody6", "nbody6++gpu", "nbody6++gpu-beijing", "nbody4"],
        default="nbody6",
        help="Specify the version of the software",
    )

    args = parser.parse_args()

    # If user provided --kz, parse that instead of reading from file
    if args.kz:
        try:
            kz_list = [int(x) for x in args.kz.split(",")]
        except ValueError:
            parser.error("--kz must be a comma-separated list of integers.")

        kz_dict = kz_mapping.get(args.version, {})

        if len(kz_list) != len(kz_dict):
            raise RuntimeError(
                f"KZ length should be {len(kz_dict)}, len={len(kz_list)} is given"
            )

        data = {"KZ": kz_list}
    else:
        # existing file-based parsing
        data = parse_input_file(args.filename, args.version)

    print_results(data, args.version)
