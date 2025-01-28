"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path

from utils.snap import get_timestamps

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

    timestamps = get_timestamps(
        nemo_file=args.nemo_file,
        n_timestamps=args.n_timestamps,
    )
    print("Printing the timestamps of a NEMO snapshot...\n\t", *timestamps)
