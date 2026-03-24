import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, text,
    Column, Integer, Float, String, MetaData, Table, ForeignKey
)
from sqlalchemy.engine import URL

load_dotenv()

# ── Connection ─────────────────────────────────────────────────────────────
url = URL.create(
    drivername="postgresql+psycopg2",
    username="daniely.santos",
    host="localhost",
    port=5432,
    database="students",
)
engine = create_engine(url)

# ── Load silver ────────────────────────────────────────────────────────────
SILVER_PATH = os.path.join(os.path.dirname(__file__), "..", "silver", "students_silver.parquet")
df = pd.read_parquet(SILVER_PATH)
df = df.reset_index(drop=True)
df["student_id"] = df.index + 1
print(f"Silver rows loaded: {len(df)}")

# ── Define Star Schema ─────────────────────────────────────────────────────
meta = MetaData()

dim_performance = Table("dim_performance", meta,
    Column("performance_id", Integer, primary_key=True),
    Column("performance_level", String(20), nullable=False, unique=True),
)

dim_student = Table("dim_student", meta,
    Column("student_id",               Integer, primary_key=True),
    Column("relationship_status",      Integer),
    Column("hostel_student",           Integer),
    Column("parental_education_level", Integer),
    Column("family_income",            Float),
    Column("internet_quality",         Float),
)

dim_lifestyle = Table("dim_lifestyle", meta,
    Column("lifestyle_id",        Integer, primary_key=True),
    Column("sleep_hours",         Float),
    Column("stress",              Float),
    Column("anxiety",             Float),
    Column("depression",          Float),
    Column("motivation",          Float),
    Column("physical_activity",   Float),
    Column("junk_food_frequency", Float),
    Column("caffeine_mg",         Float),
    Column("screen_time",         Float),
    Column("social_media_hours",  Float),
    Column("gaming_hours",        Float),
    Column("netflix_hours",       Float),
    Column("late_night_frequency",Float),
    Column("phone_unlocks_per_day",Float),
)

dim_academic = Table("dim_academic", meta,
    Column("academic_id",              Integer, primary_key=True),
    Column("study_hours",              Float),
    Column("weekly_study_sessions",    Float),
    Column("group_study_hours",        Float),
    Column("library_visits",           Float),
    Column("online_courses_completed", Integer),
    Column("class_participation",      Float),
    Column("peer_study_group",         Integer),
    Column("extracurricular_hours",    Float),
    Column("part_time_hours",          Float),
    Column("backlogs",                 Integer),
    Column("procrastination_score",    Float),
    Column("time_management",          Float),
    Column("self_discipline",          Float),
    Column("concentration",            Float),
    Column("attendance",               Float),
    Column("assignment_completion",    Float),
)

fact_performance = Table("fact_student_performance", meta,
    Column("fact_id",        Integer, primary_key=True, autoincrement=True),
    Column("student_id",     Integer, ForeignKey("dim_student.student_id"),     nullable=False),
    Column("lifestyle_id",   Integer, ForeignKey("dim_lifestyle.lifestyle_id"), nullable=False),
    Column("academic_id",    Integer, ForeignKey("dim_academic.academic_id"),   nullable=False),
    Column("performance_id", Integer, ForeignKey("dim_performance.performance_id"), nullable=False),
    Column("gpa",            Float),
    Column("midterm_score",  Float),
    Column("final_score",    Float),
    Column("project_score",  Float),
    Column("previous_gpa",   Float),
    Column("financial_stress", Float),
)

# ── Create tables (drop & recreate for idempotency) ────────────────────────
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS fact_student_performance CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS dim_student CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS dim_lifestyle CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS dim_academic CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS dim_performance CASCADE"))

meta.create_all(engine)
print("Schema created.")

# ── Populate dim_performance ───────────────────────────────────────────────
perf_levels = df["performance_level"].unique()
dim_perf_df = pd.DataFrame({
    "performance_id":    range(1, len(perf_levels) + 1),
    "performance_level": perf_levels,
})
dim_perf_df.to_sql("dim_performance", engine, if_exists="append", index=False)
perf_map = dict(zip(dim_perf_df["performance_level"], dim_perf_df["performance_id"]))

# ── Populate dim_student ───────────────────────────────────────────────────
dim_student_df = df[[
    "student_id", "relationship_status", "hostel_student",
    "parental_education_level", "family_income", "internet_quality",
]].copy()
dim_student_df.to_sql("dim_student", engine, if_exists="append", index=False)

# ── Populate dim_lifestyle ─────────────────────────────────────────────────
dim_lifestyle_df = df[[
    "sleep_hours", "stress", "anxiety", "depression", "motivation",
    "physical_activity", "junk_food_frequency", "caffeine_mg", "screen_time",
    "social_media_hours", "gaming_hours", "netflix_hours",
    "late_night_frequency", "phone_unlocks_per_day",
]].copy()
dim_lifestyle_df.insert(0, "lifestyle_id", range(1, len(dim_lifestyle_df) + 1))
dim_lifestyle_df.to_sql("dim_lifestyle", engine, if_exists="append", index=False)

# ── Populate dim_academic ─────────────────────────────────────────────────
dim_academic_df = df[[
    "study_hours", "weekly_study_sessions", "group_study_hours",
    "library_visits", "online_courses_completed", "class_participation",
    "peer_study_group", "extracurricular_hours", "part_time_hours",
    "backlogs", "procrastination_score", "time_management",
    "self_discipline", "concentration", "attendance", "assignment_completion",
]].copy()
dim_academic_df.insert(0, "academic_id", range(1, len(dim_academic_df) + 1))
dim_academic_df.to_sql("dim_academic", engine, if_exists="append", index=False)

# ── Populate fact_student_performance ─────────────────────────────────────
fact_df = df[[
    "student_id", "performance_level",
    "gpa", "midterm_score", "final_score",
    "project_score", "previous_gpa", "financial_stress",
]].copy()
fact_df["lifestyle_id"]   = dim_lifestyle_df["lifestyle_id"].values
fact_df["academic_id"]    = dim_academic_df["academic_id"].values
fact_df["performance_id"] = fact_df["performance_level"].map(perf_map)
fact_df = fact_df.drop(columns=["performance_level"])

fact_df.to_sql("fact_student_performance", engine, if_exists="append", index=False)

print(f"Gold layer loaded:")
print(f"  dim_performance          → {len(dim_perf_df):>8} rows")
print(f"  dim_student              → {len(dim_student_df):>8} rows")
print(f"  dim_lifestyle            → {len(dim_lifestyle_df):>8} rows")
print(f"  dim_academic             → {len(dim_academic_df):>8} rows")
print(f"  fact_student_performance → {len(fact_df):>8} rows")
