import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

BASE = os.path.dirname(__file__)
CHARTS_DIR = os.path.join(BASE, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

df = pd.read_parquet(os.path.join(BASE, "students_silver.parquet"))

# ── Chart 1: GPA Distribution ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df["gpa"], bins=40, color="#4C72B0", edgecolor="white")
ax.set_title("GPA Distribution")
ax.set_xlabel("GPA")
ax.set_ylabel("Count")
ax.axvline(df["gpa"].mean(), color="red", linestyle="--", label=f"Mean: {df['gpa'].mean():.2f}")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, "01_gpa_distribution.png"), dpi=120)
plt.close(fig)

# ── Chart 2: Performance Level Count ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
counts = df["performance_level"].value_counts()
bars = ax.bar(counts.index, counts.values, color=["#55A868", "#C44E52", "#8172B2"])
ax.bar_label(bars, fmt="%d")
ax.set_title("Students per Performance Level")
ax.set_xlabel("Performance Level")
ax.set_ylabel("Count")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, "02_performance_level.png"), dpi=120)
plt.close(fig)

# ── Chart 3: Study Hours vs GPA ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
sample = df.sample(min(3000, len(df)), random_state=42)
colors = {"Low": "#C44E52", "Medium": "#DD8452", "High": "#55A868"}
for level, group in sample.groupby("performance_level"):
    ax.scatter(group["study_hours"], group["gpa"],
               alpha=0.4, s=10, label=level, color=colors.get(level, "gray"))
ax.set_title("Study Hours vs GPA")
ax.set_xlabel("Study Hours")
ax.set_ylabel("GPA")
ax.legend(title="Performance")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, "03_study_hours_vs_gpa.png"), dpi=120)
plt.close(fig)

# ── Chart 4: Stress vs GPA ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
for level, group in sample.groupby("performance_level"):
    ax.scatter(group["stress"], group["gpa"],
               alpha=0.4, s=10, label=level, color=colors.get(level, "gray"))
ax.set_title("Stress Level vs GPA")
ax.set_xlabel("Stress")
ax.set_ylabel("GPA")
ax.legend(title="Performance")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, "04_stress_vs_gpa.png"), dpi=120)
plt.close(fig)

# ── Chart 5: Correlation Heatmap ─────────────────────────────────────────
key_cols = [
    "gpa", "study_hours", "attendance", "stress", "sleep_hours",
    "motivation", "procrastination_score", "final_score", "social_media_hours", "screen_time"
]
corr = df[key_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
fig.colorbar(im, ax=ax)
ax.set_xticks(range(len(key_cols)))
ax.set_yticks(range(len(key_cols)))
ax.set_xticklabels(key_cols, rotation=45, ha="right", fontsize=8)
ax.set_yticklabels(key_cols, fontsize=8)
for i in range(len(key_cols)):
    for j in range(len(key_cols)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6)
ax.set_title("Correlation Heatmap — Key Features")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, "05_correlation_heatmap.png"), dpi=120)
plt.close(fig)

print("Charts saved to:", CHARTS_DIR)

# ── Generate Markdown report ──────────────────────────────────────────────
md = """# Silver Layer — Data Analysis Charts

## 1. GPA Distribution
Histogram showing the spread of student GPA values, with the mean highlighted.

![GPA Distribution](charts/01_gpa_distribution.png)

---

## 2. Students per Performance Level
Count of students classified as Low, Medium, or High performance.

![Performance Level](charts/02_performance_level.png)

---

## 3. Study Hours vs GPA
Scatter plot coloured by performance level — shows whether more study hours correlates with higher GPA.

![Study Hours vs GPA](charts/03_study_hours_vs_gpa.png)

---

## 4. Stress Level vs GPA
Scatter plot showing the relationship between reported stress and academic performance.

![Stress vs GPA](charts/04_stress_vs_gpa.png)

---

## 5. Correlation Heatmap
Pearson correlations among 10 key features. Values near ±1 indicate strong relationships.

![Correlation Heatmap](charts/05_correlation_heatmap.png)
"""

md_path = os.path.join(BASE, "analysis_silver.md")
with open(md_path, "w") as f:
    f.write(md)

print("Markdown report saved to:", md_path)
