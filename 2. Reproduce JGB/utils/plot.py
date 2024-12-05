"""Utils used for plotting."""

import matplotlib.pyplot as plt


def create_label(mu: float, scale: float, sigma: float) -> str:
    """Creates label by log-normal model parameters."""
    if (mu, scale) == (0, 1):
        label = rf"$\sigma$ = {sigma}"
    elif (mu, scale, sigma) == (10, 1.5, 0.954):
        label = "M & A"
    else:
        label = f"{mu}_{scale}_{sigma}"

    return label


def show_with_timeout():
    """Shows a plot and automatically closes it after 10 seconds."""
    plt.show(block=False)
    plt.pause(10)
    plt.close()
