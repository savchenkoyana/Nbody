"""Utils used for plotting."""

import os
from functools import partial
from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Union

import agama
import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np


def create_label(mu: float, scale: float, sigma: float) -> str:
    """Creates label by log-normal model parameters."""
    if (mu, scale) == (0, 1):
        label = rf"$\sigma$ = {sigma}"
    elif (mu, scale, sigma) == (10, 1.5, 0.954):
        label = "M & A"
    else:
        label = f"{mu}_{scale}_{sigma}"

    return label


def create_file_label(filename: Union[str, Path]) -> str:
    """Creates label by filename.

    Filename should be like this: f'/path/to/dirname/snap_mu{mu}_s{scale}_sigma{sigma}_r{plummer_r}_N{N}_{postfix}/{name}.nemo'.
    """
    dirname = Path(filename).parts[-2]
    postfix = "_".join(dirname.split("_")[6:])

    return postfix


def show_with_timeout():
    """Shows a plot and automatically closes it after 10 seconds."""
    plt.show(block=False)
    plt.pause(10)
    plt.close()


def plot_density(
    dens: agama.Density,
    save_path: Optional[Union[str, os.PathLike]] = None,
):
    r = np.logspace(-4, 1)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, dens(xyz), linestyle="dotted")

    plt.xlabel("r, pc")
    plt.ylabel(r"$\rho, M_\odot / pc^3$")
    plt.xscale("log")
    plt.yscale("log")

    if isinstance(save_path, (str, Path)):
        plt.savefig(Path(save_path))

    show_with_timeout()


def plot_density_diff(
    orig_dens: agama.Density,
    dens: agama.Density,
    save_path: Optional[Union[str, os.PathLike]] = None,
):
    r = np.logspace(-4, 1)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, np.abs(dens(xyz) - orig_dens(xyz)) / orig_dens(xyz))

    plt.xlabel("r, pc")
    plt.ylabel(r"$\delta\rho / \rho$")
    plt.xscale("log")
    plt.yscale("log")

    if isinstance(save_path, (str, Path)):
        plt.savefig(Path(save_path))

    show_with_timeout()


def update(
    i: int,
    data: list,
    ax: plt.axes,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
):
    """Default function to update matplotlib animation."""
    (
        x,
        y,
        label,
    ) = data[i]

    ax.cla()
    ax.set(xlim=xlim, ylim=ylim)

    ax.scatter(x, y, c="b", s=2, linewidths=0)

    if label:
        ax.text(
            x=0.01,
            y=0.99,
            s=label,
            ha="left",
            va="top",
            transform=ax.transAxes,
        )


def create_animation(
    data: list,
    n_frames: int,
    fig: plt.figure,
    ax: plt.axes,
    update_animation: Optional[Callable[int, None]] = None,
    xlim: tuple[float, float] = (-40, 40),
    ylim: tuple[float, float] = (-40, 40),
    interval: int = 2000,
) -> matplotlib.animation.FuncAnimation:
    plt.rcParams["animation.html"] = "jshtml"
    plt.rcParams["animation.embed_limit"] = 200

    ax.set(xlim=xlim, ylim=ylim)

    if update_animation is None:
        update_animation = partial(
            update,
            data=data,
            ax=ax,
            xlim=xlim,
            ylim=ylim,
        )

    ani = matplotlib.animation.FuncAnimation(
        fig=fig,
        func=update_animation,
        frames=n_frames,
        interval=interval,
        cache_frame_data=True,
    )
    return ani
