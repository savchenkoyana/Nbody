"""Cut a snapshot that is too large to be stored full size."""

import argparse
import subprocess
from pathlib import Path

from utils.snap import get_timestamps

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program cuts given snapshots, only --n-timestamps of the initial data remains"
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
        default=100,
        help="The number of timestamps to use for plot. Default: 100",
    )
    args = parser.parse_args()

    if args.n_timestamps <= 0:
        raise RuntimeError("Got negative '--n-timestamps'")

    # assuming filename is: /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/<filename>.nemo
    # we will save data into /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/<filename>_cut.nemo
    filename = args.nemo_file
    save_file = filename.replace(".nemo", "_cut.nemo")

    if not Path(filename).exists():
        raise RuntimeError(f"filename {filename} does not exist")

    times_list = get_timestamps(
        filename=filename,
        n_timestamps=args.n_timestamps,
        default=True,
    )
    print("times list", times_list)

    for t in times_list:
        file_t = filename.replace(".nemo", f"_{t}")
        command = f"snaptrim in={filename} out={file_t} times={t} timefuzz=nearest"
        print(command)
        subprocess.check_call(command, shell=True)

    command = f"cat `ls -tr {filename.replace('.nemo', '')}_*` > {save_file}"
    print(command)
    subprocess.check_call(command, shell=True)
    print("Done!")
