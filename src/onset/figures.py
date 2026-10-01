"""Fig. 1A: rose plot of attack onset across the 24-h day."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PURPLE = "#8D4D9F"


def rose_plot(counts, out_stem):
    """Rose plot of hourly onset counts, saved as PDF, PNG and TIFF (600 dpi)."""
    counts = np.asarray(counts)
    fig = plt.figure(figsize=(4.2, 4.4))
    ax = fig.add_subplot(111, projection="polar")
    theta = np.deg2rad(np.arange(24) * 15)
    ax.bar(theta, counts, width=np.deg2rad(15), align="edge", color=PURPLE, edgecolor="black", linewidth=0.9, zorder=3)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 30)))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], fontsize=9)
    ticks = np.arange(5e4, counts.max(), 5e4)
    ax.set_ylim(0, ticks[-1] + 2.5e4 if len(ticks) else counts.max() * 1.1)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{int(v / 1e4)}×10$^4$" for v in ticks], fontsize=8)
    ax.set_rlabel_position(8)
    ax.grid(color="#c8c8c8", linewidth=1.2, zorder=0)
    ax.spines["polar"].set_color("#c8c8c8")
    ax.set_xlabel("Time of day (24h)", fontsize=10, labelpad=6)
    fig.text(0.03, 0.95, "A", fontsize=16, fontweight="bold")
    for ext, kw in (("pdf", {}), ("png", {"dpi": 600}), ("tiff", {"dpi": 600})):
        fig.savefig(f"{out_stem}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)
