"""Based on this jupyter-notebook: https://github.com/nbody6ppgpu/Nbody6PPGPU-beijing/blob/stable/examples/01_Basics.ipynb"""

import re
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_OUTPUT_DATA = {"RLAGR", "AVMASS", "NPARTC", "SIGR2", "SIGT2", "VROT"}

_ADJUST_DATA = {
    "T[Myr]",
    "Q",
    "DE",  # relative energy error
    "DELTA",  # absolute energy error
    "DETOT",
    "E",  # Mechanical energy: ZKIN - POT + ETIDE (E(3))
    "EKIN",
    "POT",
    "ETIDE",  # Tidal energy
    "ETOT",  # Total energy
    "EBIN",  # Binding energy of KS binaries
    "EMERGE",  # Binding energy of mergers (E(9))
    "ESUB",  # Binding energy of unperturbed triples and quadruples
    "ECOLL",  # The difference of binding energy of inner binary at the end and begin of hierarchical systems (E(10))
    "EMDOT",  # Mechanical energy of mass loss due to stellar evolution (E(12))
    "ECDOT",  # Energy of velocity kick due to stellar evolution
    "DTMIN",
    "RMIN",
    "ETAI",
    "ETAR",
    "ETAU",
}

_FULL_COLS = [
    0.001,
    0.003,
    0.005,
    0.01,
    0.03,
    0.05,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    0.95,
    0.99,
    1.0,
    "<RC",
]
_COLS = [0.01, 0.1, 0.3, 0.5, 0.9, 1.0, "<RC"]

# Precompile regexes used repeatedly
_KEYVAL_RE = re.compile(r"([A-Z]+)\s*=\s*([0-9Ee\+\-\.]+)")
_SCALING_RE = re.compile(
    r"""PHYSICAL\ SCALING:      # literal header
        \s*R\*\s*=\s*([0-9E+.\-]+)   # capture R*
        \s*M\*\s*=\s*([0-9E+.\-]+)   # capture M*
        \s*V\*\s*=\s*([0-9E+.\-]+)   # capture V*
        \s*T\*\s*=\s*([0-9E+.\-]+)   # capture T*
    """,
    re.VERBOSE,
)


def _safe_float(token: str) -> float:
    """Convert token to float safely, handling 'D' exponent and malformed
    tokens."""
    try:
        return float(token)
    except ValueError:
        try:
            return float(token.replace("D", "E"))
        except Exception:
            return np.nan


# ——— Data loading ———


def parse_log(
    logfile: Union[str, Path],
) -> Dict[str, Union[pd.DataFrame, Dict[str, pd.DataFrame], None]]:
    """Parse an Nbody6++GPU log file in one pass.

    Returns dict with keys:
      - "adjust": DataFrame (index=time)
      - "output": dict mapping data_type -> DataFrame (columns=_FULL_COLS)
      - "step": dict mapping 'I'/'R' -> DataFrame, or None if not present
      - "scaling": dict with keys 'R*','M*','V*','T*' or None
    """
    logfile = Path(logfile)
    with logfile.open("r") as fh:
        lines = fh.readlines()

    scaling = load_scaling(logfile)

    pre_etai: Optional[float] = None
    pre_etar: Optional[float] = None
    pre_etau: Optional[float] = None

    for i, raw in enumerate(lines[:50]):
        s = raw.strip()
        if s.startswith("ETAI") and "ETAR" in s:
            next_line = lines[i + 2]
            parts = next_line.split()
            pre_etai = _safe_float(parts[0])
            pre_etar = _safe_float(parts[1])
        elif s.startswith("DTMIN") and "RMIN" in s and "ETAU" in s:
            next_line = lines[i + 2]
            parts = next_line.split()
            pre_etau = _safe_float(parts[2])

    adjust_rows: List[Dict] = []
    output_rows: Dict[str, List[Tuple[float, List[float]]]] = {
        name: [] for name in _OUTPUT_DATA
    }
    step_lists: Dict[str, List[List[int]]] = {"I": [], "R": []}
    ks_params: Dict[float, Dict[str, float]] = {}
    eta_params: Dict[float, Dict[str, float]] = {}

    current_time_idx: Optional[float] = None

    # iterate once
    for i, raw in enumerate(lines):
        if not raw.strip():
            continue

        line = raw.replace("*****", " nan")
        stripped = line.strip()

        # STEP lines
        if stripped.startswith("STEP I") or stripped.startswith("STEP R"):
            parts = stripped.split()
            if len(parts) >= 2:
                step_type = parts[1]
                try:
                    values = [int(x) for x in parts[2:]]
                except ValueError:
                    continue
                if step_type in step_lists:
                    step_lists[step_type].append(values)
            continue

        # ADJUST lines
        if "ADJUST:" in line:
            toks = re.sub(r"\s+", " ", line).strip().split(" ")
            if len(toks) >= 3:
                time_token = toks[2]
                try:
                    time_val = float(time_token)
                except ValueError:
                    try:
                        time_val = float(time_token.replace("D", "E"))
                    except Exception:
                        continue
                current_time_idx = time_val
                cols = toks[3::2]
                vals_toks = toks[4::2]
                vals = [_safe_float(vt) for vt in vals_toks]
                row: Dict = {"time": time_val}
                for c, v in zip(cols, vals):
                    row[c] = v
                adjust_rows.append(row)

            # RMIN / DTMIN lines
            ks_line = lines[i + 2]
            matches = _KEYVAL_RE.findall(ks_line)
            if matches:
                params = {k: float(v) for k, v in matches if k in ("DTMIN", "RMIN")}
                if params:
                    ks_params[current_time_idx] = params

            # Explicit ETAI = ... lines override
            eta_line = lines[i + 5]
            if "ETAI" in eta_line and "=" in eta_line:
                matches = _KEYVAL_RE.findall(eta_line)
                params = {
                    k: float(v) for k, v in matches if k in ("ETAI", "ETAU", "ETAR")
                }
                pre_etai = params["ETAI"]
                pre_etar = params["ETAR"]
                pre_etau = params["ETAU"]
            else:
                params = {}
                params["ETAI"] = pre_etai
                params["ETAR"] = pre_etar
                params["ETAU"] = pre_etau

            eta_params[current_time_idx] = params

            continue

        # Output-type lines (RLAGR, AVMASS, ...)
        for data_type in _OUTPUT_DATA:
            if data_type in line:
                toks = re.sub(r"\s+", " ", raw).strip().split(" ")
                if len(toks) < 3:
                    break
                time_token = toks[0].replace("D", "E")
                try:
                    time_val = float(time_token)
                except ValueError:
                    break
                val_tokens = toks[2:]
                values = [_safe_float(vt) for vt in val_tokens]
                output_rows[data_type].append((time_val, values))
                break

    # --- Build DataFrames (keep last ADJUST row when times duplicate) ---
    # in case of terminated runs and concatenated logs
    if adjust_rows:
        df_adjust = pd.DataFrame(adjust_rows).set_index("time").sort_index()
    else:
        df_adjust = pd.DataFrame()

    # create ks/eta dataframes from collected dicts
    df_ks = pd.DataFrame.from_dict(ks_params, orient="index")
    df_eta = pd.DataFrame.from_dict(eta_params, orient="index")

    # Deduplicate the DataFrames by index, keeping the LAST occurrence
    def deduplicate(df):
        if not df.empty and not df.index.is_unique:
            df = df.groupby(level=0).last()
        return df

    df_adjust = deduplicate(df_adjust)
    df_ks = deduplicate(df_ks)
    df_eta = deduplicate(df_eta)

    # Now safe to concat
    if not df_adjust.empty:
        df_adjust = pd.concat([df_adjust, df_ks, df_eta], axis=1)
    else:
        df_adjust = (
            pd.concat([df_ks, df_eta], axis=1)
            if (not df_ks.empty or not df_eta.empty)
            else pd.DataFrame()
        )

    output_result: Dict[str, pd.DataFrame] = {}
    for data_type, rows in output_rows.items():
        if not rows:
            output_result[data_type] = pd.DataFrame(columns=_FULL_COLS)
            continue
        times, vals_list = zip(*rows)
        df = pd.DataFrame(vals_list, index=pd.Index(times, name="time"))
        expected_n = len(_FULL_COLS)
        if df.shape[1] < expected_n:
            for i in range(df.shape[1], expected_n):
                df[i] = np.nan
        elif df.shape[1] > expected_n:
            df = df.iloc[:, :expected_n]
        df.columns = _FULL_COLS
        df.sort_index(inplace=True)
        output_result[data_type] = df

    # Build step dataframes only if there is STEP content
    any_step_found = any(len(lst) > 0 for lst in step_lists.values())
    if any_step_found:
        step_dfs: Dict[str, pd.DataFrame] = {}
        for key, rows in step_lists.items():
            if not rows:
                continue
            maxlen = max(len(r) for r in rows)
            cols = [f"bin_{i}" for i in range(maxlen)]
            normalized = [r + [np.nan] * (maxlen - len(r)) for r in rows]
            step_dfs[key] = pd.DataFrame(normalized, columns=cols)
    else:
        step_dfs = None  # explicitly indicate absence

    return {
        "adjust": df_adjust,
        "output": output_result,
        "step": step_dfs,
        "scaling": scaling,
    }


def load_scaling(logfile: str):
    """Get scale coefficient from log file."""
    pat = re.compile(
        r"""PHYSICAL\ SCALING:      # literal header
            \s*R\*\s*=\s*([0-9E+.\-]+)   # capture R*
            \s*M\*\s*=\s*([0-9E+.\-]+)   # capture M*
            \s*V\*\s*=\s*([0-9E+.\-]+)   # capture V*
            \s*T\*\s*=\s*([0-9E+.\-]+)   # capture T*
        """,
        re.VERBOSE,
    )

    with open(logfile) as nb_stdout:
        for line in nb_stdout:
            m = re.search(pat, line)
            if m:
                keys = ["R*", "M*", "V*", "T*"]
                vals = map(float, m.groups())
                return dict(zip(keys, vals))


def load_data(logfile: Union[str, Path]):
    return parse_log(logfile)


# ——— Data plotting ———


def plot_adjust_data(
    df: pd.DataFrame,
    plot_values: list,
    logscale: bool,
    ax: Optional[matplotlib.axes._axes.Axes] = None,
):
    """Plot data produced at 'adjust' stage.

    Y axis can be in default scale or logscale. Only N-body units are
    supported.
    """
    if ax is None:
        fig = plt.figure(figsize=(9, 6))
        ax = fig.gca()

    df[plot_values].plot(ax=ax)

    ax.set_title(r"Energy evolution")
    ax.set_xlabel(r"Time t [nbody units]")
    ax.set_ylabel(r"Energy E [nbody units]")
    ax.grid()
    if logscale:
        ax.set_yscale("log")
    return ax.figure, ax


def plot_output_data(data: dict, plot_values: list, astro_units: bool):
    """Plot data produced at 'output' stage.

    Both N-body units and astro units are supported.
    """
    if astro_units:
        data["RLAGR"] *= data["R*"]
        data["AVMASS"] *= data["M*"]
        data["SIGR2"] *= data["V*"]
        data["SIGT2"] *= data["V*"]
        data["VROT"] *= data["V*"]

    N = len(plot_values)
    # choose columns close to square
    n_cols = np.ceil(np.sqrt(N)).astype(np.int32)
    n_rows = np.ceil(N / n_cols).astype(np.int32)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows))
    axes = np.atleast_1d(axes).flatten()

    for ax, pdata in zip(axes, plot_values):
        ax.set_title(f"{pdata} time evolution")
        for col in _COLS:
            y = data[pdata][col]
            x = np.arange(y.size)
            if astro_units:
                x = x * data["T*"]  # here we assume that deltat=1.0, TODO: rewrite
            ax.plot(x, y, label=col)

        if astro_units:
            ax.set_xlabel(r"Time t [Myr]")
            ax.set_ylabel(rf"{pdata} [astro units]")
        else:
            ax.set_xlabel(r"Time t [nbody units]")
            ax.set_ylabel(rf"{pdata} [nbody units]")

        ax.grid()

        if pdata != "VROT":
            ax.set_yscale("log")

    for ax in axes[N:]:
        ax.set_visible(False)

    fig.tight_layout()
    plt.legend()
    return fig, ax
