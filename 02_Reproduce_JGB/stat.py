"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path
from typing import Union

import numpy as np
import unsio.input as uns_in


def generate_timestamps(nemo_file: Union[str, Path]):
    fp_uns = uns_in.CUNS_IN(str(nemo_file), float32=True)

    while fp_uns.nextFrame("mxv"):
        yield fp_uns.getData("time")[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program prints statistics for a given NEMO snapshot"
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Nemo file",
    )
    parser.add_argument(
        "--n-timestamps",
        type=int,
        default=10,
        help="The number of timestamps to return. Default: 10",
    )
    args = parser.parse_args()

    # Sanity checks
    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")
    if args.n_timestamps <= 0:
        raise RuntimeError(
            f"--n-timestamps should be positive, got {args.n_timestamps}"
        )

    print("Printing the timestamps of a NEMO snapshot...")
    timestamps = [_ for _ in generate_timestamps(filename)]

    indices = [
        _ * len(timestamps) // args.n_timestamps for _ in range(args.n_timestamps)
    ]
    chosen_timestamps = np.array(timestamps)[indices]

    print("\t", *chosen_timestamps)
