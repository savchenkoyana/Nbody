import argparse
from pathlib import Path

import numpy as np
from utils.nbody6_log import load_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Checks energy conservation")
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Path to directory with experiment",
    )
    args = parser.parse_args()
    exp = Path(args.exp)
    df_adjust = load_data(exp / "exp.out")["adjust"]

    print(f"max(DE) = {np.max(np.abs(df_adjust['DE']))}")
    print(f"max(DETOT) = {np.max(np.abs(df_adjust['DETOT']))}")
    print(f"DETOT = {df_adjust['DETOT'].iloc[-1]}")
