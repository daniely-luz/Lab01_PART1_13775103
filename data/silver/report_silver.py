import os
import pandas as pd

# ── Load silver parquet ────────────────────────────────────────────────────
parquet_path = os.path.join(os.path.dirname(__file__), "students_silver.parquet")
df = pd.read_parquet(parquet_path)

lines = []
lines.append("# Silver Layer Report — students\n")
lines.append(f"Rows: {len(df)}  |  Columns: {len(df.columns)}\n")

# ── Column types ───────────────────────────────────────────────────────────
lines.append("\n## Column Types\n")
lines.append(f"{'Column':<40} {'Type'}\n")
lines.append(f"{'-'*40} {'-'*15}\n")
for col, dtype in df.dtypes.items():
    lines.append(f"{col:<40} {dtype}\n")

# ── Null counts ────────────────────────────────────────────────────────────
lines.append("\n## Null Counts\n")
null_counts = df.isnull().sum()
has_nulls = null_counts[null_counts > 0]
if has_nulls.empty:
    lines.append("No null values found.\n")
else:
    lines.append(f"{'Column':<40} {'Nulls'}\n")
    lines.append(f"{'-'*40} {'-'*10}\n")
    for col, count in has_nulls.items():
        lines.append(f"{col:<40} {count}\n")

# ── Descriptive statistics ─────────────────────────────────────────────────
lines.append("\n## Descriptive Statistics (numeric columns)\n")
stats = df.select_dtypes(include="number").agg(["mean", "std", "min", "max"]).T.round(4)
lines.append(stats.to_string())
lines.append("\n")

# ── Save report ────────────────────────────────────────────────────────────
report_path = os.path.join(os.path.dirname(__file__), "students_silver_report.txt")
with open(report_path, "w") as f:
    f.writelines(lines)

print(f"Report saved → {report_path}")
