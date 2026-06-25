import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/study_export_without_attention_check_with_order.csv")
slider_df = df[df["Condition"] == "slider"]

CONTROL_AVG_TIME = 59.2  # from the control LMM intercept

summary = (
    slider_df.groupby("Slider Interactions")
    .agg(
        n_trials=("Duration", "size"),
        avg_time=("Duration", "mean"),
        avg_query_searches=("Query Searches", "mean"),
    )
    .reset_index()
)

summary["diff_vs_control"] = summary["avg_time"] - CONTROL_AVG_TIME

print(summary.to_string(index=False))

# === Query Searches breakdown for trials with 0 slider interactions ===
zero_slider_df = slider_df[slider_df["Slider Interactions"] == 0]
query_counts = (
    zero_slider_df.groupby("Query Searches").size().reset_index(name="n_trials")
)
print("\nQuery Searches breakdown (Slider Interactions == 0):")
print(query_counts.to_string(index=False))

zero_slider_df.to_csv("slider_zero_interactions.csv", index=False)
print(
    "\nSaved filtered trials (slider condition, 0 slider interactions) to slider_zero_interactions.csv"
)

# === Bar chart: Task Order counts for 0 slider interaction trials ===
task_order_counts = zero_slider_df["Task Order"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6, 5))
ax.bar(task_order_counts.index.astype(str), task_order_counts.values)
ax.set_xlabel("Task Order")
ax.set_ylabel("Number of Trials")
ax.set_title("Task Order Counts (Slider Interactions == 0)")
plt.tight_layout()


# === Task ID frequency for 0 slider interaction trials ===
TASK_ID_NAMES = {
    285114: "Airplane",
    144243: "Soccer",
    200212: "Trams",
    403710: "Surfer",
}

task_id_counts = zero_slider_df["Task ID"].value_counts().sort_index()
task_id_labels = task_id_counts.index.map(TASK_ID_NAMES)
print("\nTask ID frequency (Slider Interactions == 0):")
print(
    pd.DataFrame(
        {
            "Task ID": task_id_counts.index,
            "Task Name": task_id_labels,
            "n_trials": task_id_counts.values,
        }
    ).to_string(index=False)
)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(task_id_labels, task_id_counts.values)
ax.set_xlabel("Task")
ax.set_ylabel("Number of Trials")
ax.set_title("Task ID Frequency (Slider Interactions == 0)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()


# === Success/Failure split per task for 0 slider interaction trials ===
# Deliberate palette: a muted slate-teal for success, warm clay for failure -
# both desaturated enough to read calmly side by side and reproduce fine
# in greyscale print (different lightness, not just different hue).
SUCCESS_COLOR = "#3B6E71"  # muted slate-teal
FAILURE_COLOR = "#D98C5F"  # warm clay

success_by_task = (
    zero_slider_df.groupby(["Task ID", "Success"]).size().unstack(fill_value=0)
)
success_by_task = success_by_task.reindex(columns=[1, 0], fill_value=0)
success_by_task.index = success_by_task.index.map(TASK_ID_NAMES)

fig, ax = plt.subplots(figsize=(8, 5.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

bars_success = ax.bar(
    success_by_task.index,
    success_by_task[1],
    color=SUCCESS_COLOR,
    label="Success",
    width=0.6,
    edgecolor="white",
    linewidth=0.8,
)
bars_failure = ax.bar(
    success_by_task.index,
    success_by_task[0],
    bottom=success_by_task[1],
    color=FAILURE_COLOR,
    label="Failure",
    width=0.6,
    edgecolor="white",
    linewidth=0.8,
)

# Value labels inside each segment, only when the segment is tall enough to hold one
for bars in (bars_success, bars_failure):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                str(int(height)),
                ha="center",
                va="center",
                color="white",
                fontsize=10,
                fontweight="bold",
            )

ax.set_xlabel("Task", fontsize=11, labelpad=10)
ax.set_ylabel("Number of Trials", fontsize=11, labelpad=10)
ax.set_title(
    "Success vs Failure per Task\n(Slider Condition, 0 Slider Interactions)",
    fontsize=13,
    fontweight="bold",
    pad=14,
)
ax.legend(frameon=False, fontsize=10, loc="upper right")

# Clean up chart borders - keep only the bottom axis line
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#888888")
ax.tick_params(axis="x", labelsize=10.5, length=0)
ax.tick_params(axis="y", labelsize=10)
ax.yaxis.grid(True, color="#E5E5E5", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()
# === Boxplot: distribution of Slider Interactions, slider condition only ===
fig, ax = plt.subplots(figsize=(5, 6))
ax.boxplot(
    slider_df["Slider Interactions"],
    vert=True,
    showmeans=True,
    meanprops={
        "marker": "D",
        "markerfacecolor": "red",
        "markeredgecolor": "red",
        "markersize": 8,
    },
)
ax.set_ylabel("Slider Interactions per trial")
ax.set_title("Slider Interaction Counts (Slider Condition)")
ax.set_xticks([])
plt.tight_layout()
