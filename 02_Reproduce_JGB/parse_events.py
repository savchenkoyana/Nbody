import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

_EVENT_TYPE = yaml.safe_load(open("utils/nbody6_events.yaml"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Parses event.35 data (KZ(19) or KZ(27) should be actuvated during simulation!)."
    )
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Path to directory with event.35 file",
    )
    args = parser.parse_args()
    exp = Path(args.exp)

    df = pd.read_csv(exp / "event.35", sep=r"\s+", skiprows=[0], header=None)
    df_col = pd.read_csv(exp / "event.35")
    colnames = list(df_col.columns)[0].split()
    colnames_last = colnames[-1]
    colnames = colnames[:-1] + [f"{colnames_last}_{i}" for i in range(16)]
    df.columns = colnames

    for column in set(_EVENT_TYPE.keys()).intersection(df.columns):
        event_counter = df[column].unique()
        print(f"{column}: {np.max(event_counter)} ({_EVENT_TYPE[column]})")
        if len(event_counter) > 1:
            for i in event_counter[1:]:
                print(f"\t Event {i} happened at T[NB]={df[df[column] == i].index[0]}")
