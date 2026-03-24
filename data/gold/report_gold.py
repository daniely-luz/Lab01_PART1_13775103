"""
Gold Layer — Business Questions
Each function queries the Star Schema and returns a formatted DataFrame.
"""
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

url = URL.create(
    drivername="postgresql+psycopg2",
    username="daniely.santos",
    host="localhost",
    port=5432,
    database="students",
)
engine = create_engine(url)


def q1_avg_gpa_by_performance() -> pd.DataFrame:
    """
    Q1: What is the average GPA, final score, and student count
        per performance level?
    """
    sql = """
        SELECT
            p.performance_level,
            COUNT(*)                    AS total_students,
            ROUND(AVG(f.gpa)::numeric, 2)          AS avg_gpa,
            ROUND(AVG(f.final_score)::numeric, 2)  AS avg_final_score,
            ROUND(AVG(f.midterm_score)::numeric, 2) AS avg_midterm_score
        FROM fact_student_performance f
        JOIN dim_performance p USING (performance_id)
        GROUP BY p.performance_level
        ORDER BY avg_gpa DESC
    """
    return pd.read_sql(text(sql), engine)


def q2_lifestyle_impact_on_gpa() -> pd.DataFrame:
    """
    Q2: How do average stress, sleep hours, and screen time differ
        across performance levels?
    Answers: which lifestyle habits most affect academic performance.
    """
    sql = """
        SELECT
            p.performance_level,
            ROUND(AVG(l.stress)::numeric, 2)        AS avg_stress,
            ROUND(AVG(l.sleep_hours)::numeric, 2)   AS avg_sleep_hours,
            ROUND(AVG(l.screen_time)::numeric, 2)   AS avg_screen_time,
            ROUND(AVG(l.social_media_hours)::numeric, 2) AS avg_social_media_hours,
            ROUND(AVG(l.motivation)::numeric, 2)    AS avg_motivation
        FROM fact_student_performance f
        JOIN dim_performance p USING (performance_id)
        JOIN dim_lifestyle   l USING (lifestyle_id)
        GROUP BY p.performance_level
        ORDER BY avg_stress DESC
    """
    return pd.read_sql(text(sql), engine)


def q3_academic_habits_by_performance() -> pd.DataFrame:
    """
    Q3: What are the average study hours, attendance, and procrastination
        score per performance level?
    Answers: which academic behaviours predict high performance.
    """
    sql = """
        SELECT
            p.performance_level,
            ROUND(AVG(a.study_hours)::numeric, 2)           AS avg_study_hours,
            ROUND(AVG(a.attendance)::numeric, 2)            AS avg_attendance,
            ROUND(AVG(a.assignment_completion)::numeric, 2) AS avg_assignment_completion,
            ROUND(AVG(a.procrastination_score)::numeric, 2) AS avg_procrastination,
            ROUND(AVG(a.backlogs)::numeric, 2)              AS avg_backlogs
        FROM fact_student_performance f
        JOIN dim_performance p USING (performance_id)
        JOIN dim_academic    a USING (academic_id)
        GROUP BY p.performance_level
        ORDER BY avg_study_hours DESC
    """
    return pd.read_sql(text(sql), engine)


def q4_financial_background_vs_gpa() -> pd.DataFrame:
    """
    Q4: Does family income or parental education level influence GPA?
    Groups students into income terciles and shows average GPA per group.
    """
    sql = """
        WITH percentiles AS (
            SELECT
                PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY family_income) AS p33,
                PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY family_income) AS p66
            FROM dim_student
        )
        SELECT
            CASE
                WHEN s.family_income < pc.p33 THEN 'Low Income'
                WHEN s.family_income < pc.p66 THEN 'Mid Income'
                ELSE 'High Income'
            END AS income_group,
            s.parental_education_level,
            ROUND(AVG(f.gpa)::numeric, 2)         AS avg_gpa,
            ROUND(AVG(f.final_score)::numeric, 2)  AS avg_final_score,
            COUNT(*)                                AS total_students
        FROM fact_student_performance f
        JOIN dim_student s USING (student_id)
        CROSS JOIN percentiles pc
        GROUP BY income_group, s.parental_education_level
        ORDER BY income_group, s.parental_education_level
    """
    return pd.read_sql(text(sql), engine)


def q5_top10_high_performers_profile() -> pd.DataFrame:
    """
    Q5: What is the profile of the top 10% GPA students vs bottom 10%?
    Compares key lifestyle and academic metrics between the two extremes.
    """
    sql = """
        WITH ranked AS (
            SELECT
                f.fact_id,
                f.gpa,
                f.financial_stress,
                a.study_hours,
                a.attendance,
                a.procrastination_score,
                l.stress,
                l.sleep_hours,
                l.motivation,
                NTILE(10) OVER (ORDER BY f.gpa) AS decile
            FROM fact_student_performance f
            JOIN dim_academic  a USING (academic_id)
            JOIN dim_lifestyle l USING (lifestyle_id)
        )
        SELECT
            CASE WHEN decile = 10 THEN 'Top 10%' ELSE 'Bottom 10%' END AS group,
            COUNT(*)                                    AS students,
            ROUND(AVG(gpa)::numeric, 2)                AS avg_gpa,
            ROUND(AVG(study_hours)::numeric, 2)        AS avg_study_hours,
            ROUND(AVG(attendance)::numeric, 2)         AS avg_attendance,
            ROUND(AVG(procrastination_score)::numeric, 2) AS avg_procrastination,
            ROUND(AVG(stress)::numeric, 2)             AS avg_stress,
            ROUND(AVG(sleep_hours)::numeric, 2)        AS avg_sleep,
            ROUND(AVG(motivation)::numeric, 2)         AS avg_motivation
        FROM ranked
        WHERE decile IN (1, 10)
        GROUP BY "group"
        ORDER BY avg_gpa DESC
    """
    return pd.read_sql(text(sql), engine)


# ── Run all questions ──────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        ("Q1 — Average GPA by Performance Level",        q1_avg_gpa_by_performance),
        ("Q2 — Lifestyle Impact on GPA",                 q2_lifestyle_impact_on_gpa),
        ("Q3 — Academic Habits by Performance Level",    q3_academic_habits_by_performance),
        ("Q4 — Financial Background vs GPA",             q4_financial_background_vs_gpa),
        ("Q5 — Top 10% vs Bottom 10% Student Profile",   q5_top10_high_performers_profile),
    ]

    lines = []
    lines.append("GOLD LAYER — BUSINESS QUESTIONS REPORT\n")
    lines.append("=" * 60 + "\n\n")

    for title, fn in questions:
        header = f"  {title}"
        lines.append("=" * 60 + "\n")
        lines.append(header + "\n")
        lines.append("=" * 60 + "\n")
        result = fn()
        lines.append(result.to_string(index=False) + "\n\n")
        print(header)
        print(result.to_string(index=False))

    report_path = os.path.join(os.path.dirname(__file__), "business_report_gold.txt")
    with open(report_path, "w") as f:
        f.writelines(lines)

    print(f"\nReport saved → {report_path}")
