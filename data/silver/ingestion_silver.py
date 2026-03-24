import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

# ── 1. Read from raw layer ─────────────────────────────────────────────────
url = URL.create(
    drivername="postgresql+psycopg2",
    username="daniely.santos",
    host="localhost",
    port=5432,
    database="students",
)
engine = create_engine(url)

df = pd.read_sql_table("students", engine)
print(f"Raw rows loaded: {len(df)}")

# ── 2. Standardise column names → snake_case ───────────────────────────────
def to_snake_case(name: str) -> str:
    name = re.sub(r"[\s\-]+", "_", name.strip())
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()

df.columns = [to_snake_case(c) for c in df.columns]

# ── 3. Remove duplicates ───────────────────────────────────────────────────
before = len(df)
df = df.drop_duplicates()
print(f"Duplicates removed: {before - len(df)}")

# ── 4. Handle missing values ───────────────────────────────────────────────
numeric_cols = df.select_dtypes(include="number").columns
categorical_cols = df.select_dtypes(include="object").columns

df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
df[categorical_cols] = df[categorical_cols].fillna("unknown")

print(f"Nulls after imputation: {df.isnull().sum().sum()}")

# ── 5. Convert string columns that look like dates ─────────────────────────
date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}")
for col in categorical_cols:
    sample = df[col].dropna().head(20)
    if sample.apply(lambda v: bool(date_pattern.match(str(v)))).all():
        df[col] = pd.to_datetime(df[col], errors="coerce")
        print(f"Converted to datetime: {col}")

# ── 6. Save as Parquet ─────────────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(__file__))
output_path = os.path.join(output_dir, "students_silver.parquet")

df.to_parquet(output_path, index=False)
print(f"Silver layer saved → {output_path} ({len(df)} rows, {len(df.columns)} cols)")
