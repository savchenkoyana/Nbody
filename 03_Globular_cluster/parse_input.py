"""Parses NbodyX input to give human-readable summary.

Warning, created using vibe-coding!
"""

import argparse

from config import _NBODY4_CONFIG
from config import _NBODY6_CONFIG
from config import _NBODY6GPU_CONFIG

# Dictionary to store descriptions for different versions
kz_descriptions = {
    "nbody4": _NBODY4_CONFIG,
    "nbody6": _NBODY6_CONFIG,
    "nbody6++gpu": _NBODY6GPU_CONFIG,
}


def parse_nbody6(lines):
    data = {}

    data["KSTART"], data["TCOMP"] = map(float, lines[0].split())
    (
        data["N"],
        data["NFIX"],
        data["NCRIT"],
        data["NRAND"],
        data["NNBMAX"],
        data["NRUN"],
    ) = map(int, lines[1].split())

    (
        data["ETAI"],
        data["ETAR"],
        data["RS0"],
        data["DTADJ"],
        data["DELTAT"],
        data["TCRIT"],
        data["QE"],
        data["RBAR"],
        data["ZMBAR"],
    ) = map(float, lines[2].split())

    kz_flat_list = [list(map(int, line.split())) for line in lines[3:8]]
    data["KZ"] = [kz for sublist in kz_flat_list for kz in sublist]

    (
        data["DTMIN"],
        data["RMIN"],
        data["ETAU"],
        data["ECLOSE"],
        data["GMIN"],
        data["GMAX"],
    ) = map(float, lines[8].split())

    (
        data["ALPHA"],
        data["BODY1"],
        data["BODYN"],
        data["NBIN0"],
        data["NHI0"],
        data["ZMET"],
        data["EPOCH0"],
        data["DTPLOT"],
    ) = map(float, lines[9].split())

    (data["Q"], data["VXROT"], data["VZROT"], data["RTIDE"], data["SMAX"]) = map(
        float, lines[10].split()
    )

    # TODO: parse next lines!
    return data


def parse_nbody4(lines):
    data = {}

    data["KSTART"], data["TCOMP"], data["GPID"] = map(float, lines[0].split())
    (
        data["N"],
        data["NFIX"],
        data["NCRIT"],
        data["NRAND"],
        data["NRUN"],
    ) = map(int, lines[1].split())

    (
        data["ETA"],
        data["DTADJ"],
        data["DELTAT"],
        data["TCRIT"],
        data["QE"],
        data["RBAR"],
        data["ZMBAR"],
    ) = map(float, lines[2].split())

    kz_flat_list = [list(map(int, line.split())) for line in lines[3:7]]
    data["KZ"] = [kz for sublist in kz_flat_list for kz in sublist]

    (
        data["DTMIN"],
        data["RMIN"],
        data["ETAU"],
        data["ECLOSE"],
        data["GMIN"],
        data["GMAX"],
    ) = map(float, lines[7].split())

    (
        data["ALPHA"],
        data["BODY1"],
        data["BODYN"],
        data["NBIN0"],
        data["ZMET"],
        data["EPOCH0"],
        data["DTPLOT"],
    ) = map(float, lines[8].split())

    (data["Q"], data["VXROT"], data["VZROT"], data["RTIDE"]) = map(
        float, lines[9].split()
    )

    # TODO: parse next lines!
    return data


def parse_input_file(filename, version):
    with open(filename) as file:
        lines = [line.strip() for line in file if line.strip()]

    lines = [line.replace("D", "E") for line in lines]

    if version == "nbody6":
        return parse_nbody6(lines)
    elif version == "nbody6++gpu":
        pass
    elif version == "nbody4":
        return parse_nbody4(lines)


def print_results(data, version):
    print("Non-zero KZ parameters:")
    kz_dict = kz_descriptions.get(version, {})
    for i, value in enumerate(data["KZ"], start=1):
        if value != 0:
            meaning = kz_dict.get(i, "Unknown KZ option")
            print(f"  KZ{i}: {value} ({meaning})")

    print("\nOther parameters:")
    for key, value in data.items():
        if key != "KZ":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse an input file and extract relevant parameters."
    )
    parser.add_argument("filename", type=str, help="Path to the input file")
    parser.add_argument(
        "--version",
        type=str,
        choices=["nbody6", "nbody6++gpu", "nbody4"],
        default="nbody6",
        help="Specify the version of the software",
    )

    args = parser.parse_args()

    if args.version not in ["nbody6", "nbody4"]:
        raise NotImplementedError(f"Version '{args.version}' is not implemented yet.")

    data = parse_input_file(args.filename, args.version)
    print_results(data, args.version)
