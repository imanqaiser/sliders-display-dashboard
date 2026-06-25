import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("data/study_export_without_attention_check_with_order.csv")

control = df[df["Condition"] == "control"]
slider = df[df["Condition"] == "slider"]

# Shared bins so both figures are visually comparable
bin_max = df["Duration"].max()
bins = np.linspace(0, bin_max, 25)

CONTROL_COLOR = "#0b5da2"
NO_SLIDER_COLOR = "#c94905"
USED_SLIDER_COLOR = "#0b5da2"


def style_axis(ax):
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.yaxis.grid(True, color="#E5E5E5", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


# ============================================================
# Figure 1: Control task times
# ============================================================
fig1, ax1 = plt.subplots(figsize=(8, 5.5))
fig1.patch.set_facecolor("white")
ax1.set_facecolor("white")

ax1.hist(
    control["Duration"],
    bins=bins,
    color=CONTROL_COLOR,
    edgecolor="white",
    linewidth=0.6,
)

ax1.set_xlabel("Task Duration (seconds)", fontsize=11, labelpad=10)
ax1.set_ylabel("Number of Trials", fontsize=11, labelpad=10)
ax1.set_title(
    f"Control Task Times (n={len(control)})", fontsize=13, fontweight="bold", pad=14
)
style_axis(ax1)

plt.tight_layout()
plt.savefig("control_duration_histogram.png", dpi=150)
print("Saved control_duration_histogram.png")

# ============================================================
# Figure 2: Slider task times, stratified by used vs didn't use sliders
# Overlapping semi-transparent histograms instead of stacked bars -
# stacked bars (like the reference image) hide each subgroup's actual
# shape since the top group floats on an uneven baseline.
# ============================================================
slider = slider.copy()
slider["Used Sliders"] = np.where(
    slider["Slider Interactions"] > 0, "Used sliders", "0 sliders"
)

used = slider[slider["Used Sliders"] == "Used sliders"]
not_used = slider[slider["Used Sliders"] == "0 sliders"]

fig2, ax2 = plt.subplots(figsize=(8, 5.5))
fig2.patch.set_facecolor("white")
ax2.set_facecolor("white")

# Compute counts per bin for both groups first, so we can decide per-bin
# which one is shorter and should be drawn on top (instead of always
# drawing one color over the other regardless of height).
not_used_counts, _ = np.histogram(not_used["Duration"], bins=bins)
used_counts, _ = np.histogram(used["Duration"], bins=bins)
bin_width = bins[1] - bins[0]

for i in range(len(bins) - 1):
    left = bins[i]
    nu_h = not_used_counts[i]
    u_h = used_counts[i]

    # Draw taller bar first, shorter bar second (on top) so the smaller
    # value is never hidden behind the larger one in this bin.
    if nu_h >= u_h:
        order = [(nu_h, NO_SLIDER_COLOR), (u_h, USED_SLIDER_COLOR)]
    else:
        order = [(u_h, USED_SLIDER_COLOR), (nu_h, NO_SLIDER_COLOR)]

    for height, color in order:
        if height > 0:
            ax2.bar(
                left,
                height,
                width=bin_width,
                align="edge",
                color=color,
                alpha=0.8,
                edgecolor="white",
                linewidth=0.6,
                zorder=2,
            )

# Dummy patches just to build a clean legend (since bars were drawn per-bin above)
from matplotlib.patches import Patch

legend_handles = [
    Patch(facecolor=NO_SLIDER_COLOR, alpha=0.8, label=f"0 sliders (n={len(not_used)})"),
    Patch(
        facecolor=USED_SLIDER_COLOR, alpha=0.8, label=f"Used sliders (n={len(used)})"
    ),
]

ax2.set_xlabel("Task Duration (seconds)", fontsize=11, labelpad=10)
ax2.set_ylabel("Number of Trials", fontsize=11, labelpad=10)
ax2.set_title(
    f"Slider Task Times by Slider Use (n={len(slider)})",
    fontsize=13,
    fontweight="bold",
    pad=14,
)
ax2.legend(handles=legend_handles, frameon=False, fontsize=10)
style_axis(ax2)

plt.tight_layout()
plt.savefig("slider_duration_histogram_stratified.png", dpi=150)
print("Saved slider_duration_histogram_stratified.png")
