"""Print statistics for a given NEMO snapshot."""

import argparse
from pathlib import Path
from typing import Union

import unsio.input as uns_in


def generate_timestamps(
    nemo_file: Union[str, Path],
    frame_step: int = 1000,
):
    fp_uns = uns_in.CUNS_IN(str(nemo_file), float32=True)
    frame_num = 0

    while fp_uns.nextFrame("mxv"):
        t = fp_uns.getData("time")[1]
        if frame_num % frame_step == 0:
            yield t

        frame_num += 1


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
    args = parser.parse_args()

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")

    print("Printing the timestamps of a NEMO snapshot...")
    timestamps = [_ for _ in generate_timestamps(filename)]
    print("\t", *timestamps)
