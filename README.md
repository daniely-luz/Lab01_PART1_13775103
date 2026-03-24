# Lab01 — Medallion Architecture: College Students Habits & Performance

**Dataset:** [College Students Habits and Performance](https://www.kaggle.com/datasets/sharmajicoder/college-students-habits-and-performance)
**Rows:** 1,000,000 | **Columns:** 42 | **Source:** Kaggle (synthetic)

---

## 1. Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│   Kaggle    │────►│   RAW Layer      │────►│   SILVER Layer      │────►│   GOLD Layer         │
│  (Source)   │     │  PostgreSQL      │     │   Parquet file      │     │  PostgreSQL           │
│             │     │  table: students │     │  students_silver    │     │  Star Schema          │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────────────┘
      │                     │                         │                            │
  kagglehub            ingestion_raw.py          ingestion_silver.py        ingestion_gold.py
  download             raw insert                clean + parquet            dim + fact tables
```

**Flow:**
`Kaggle API` → `Python (kagglehub)` → `PostgreSQL raw table` → `Parquet (Silver)` → `PostgreSQL Star Schema (Gold)`

---

## 2. Scripts

### `data/raw/ingestion_raw.py` — Raw Layer
Downloads the dataset from Kaggle via `kagglehub` and inserts all rows as-is into the `students` table in PostgreSQL. No transformations are applied at this stage.

### `data/silver/ingestion_silver.py` — Silver Layer
Reads the raw `students` table from PostgreSQL and applies:
- Snake_case column name standardisation
- Duplicate removal
- Missing value imputation (median for numeric, `"unknown"` for categorical)
- Automatic date detection and conversion
- Saves result to `data/silver/students_silver.parquet`

### `data/silver/report_silver.py` — Silver Report
Reads the silver Parquet and generates [`data/silver/students_silver_report.txt`](data/silver/students_silver_report.txt) with:
- Row/column count
- Column types
- Null counts
- Descriptive statistics (mean, std, min, max)

### `data/silver/chart_silver.py` — Silver Charts
Generates 5 analysis charts and saves them to `data/silver/charts/`.
Full analysis available in [`data/silver/analysis_silver.md`](data/silver/analysis_silver.md):

| Chart | Description |
|-------|-------------|
| GPA Distribution | Histogram of GPA values with mean line |
| Performance Level | Bar chart — student count per level (Low/Medium/High) |
| Study Hours vs GPA | Scatter plot coloured by performance level |
| Stress vs GPA | Scatter plot — stress impact on academic performance |
| Correlation Heatmap | Pearson correlations among 10 key features |

### `data/gold/ingestion_gold.py` — Gold Layer (Star Schema)
Reads the silver Parquet and loads a Star Schema into PostgreSQL:

```
fact_student_performance
  ├── dim_performance   (performance_level)
  ├── dim_student       (demographics: income, hostel, parental education)
  ├── dim_lifestyle     (sleep, stress, screen time, social media...)
  └── dim_academic      (study hours, attendance, backlogs, procrastination...)
```

### `data/gold/report_gold.py` — Business Questions
5 business functions querying the Star Schema. Results saved to [`data/gold/business_report_gold.txt`](data/gold/business_report_gold.txt).

---

## 3. Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| `study_hours` | float | Daily hours dedicated to studying |
| `attendance` | float | Class attendance percentage (0–100) |
| `assignment_completion` | float | Percentage of assignments completed (0–100) |
| `midterm_score` | float | Midterm exam score (0–100) |
| `final_score` | float | Final exam score (0–100) |
| `project_score` | float | Project score (0–100) |
| `backlogs` | int | Number of failed/pending subjects |
| `sleep_hours` | float | Average nightly sleep hours |
| `stress` | float | Self-reported stress level (1–10) |
| `anxiety` | float | Anxiety score (0–100) |
| `depression` | float | Depression score (0–100) |
| `motivation` | float | Motivation score (1–10) |
| `concentration` | float | Concentration ability score (1–10) |
| `time_management` | float | Time management score (1–10) |
| `self_discipline` | float | Self-discipline score (1–10) |
| `social_media_hours` | float | Daily hours on social media |
| `gaming_hours` | float | Daily hours gaming |
| `netflix_hours` | float | Daily hours watching streaming content |
| `screen_time` | float | Total daily screen time (hours) |
| `physical_activity` | float | Weekly physical activity (hours) |
| `junk_food_frequency` | float | Junk food consumption per week |
| `caffeine_mg` | float | Daily caffeine intake in mg |
| `late_night_frequency` | float | Frequency of staying up late per week |
| `procrastination_score` | float | Procrastination tendency (1–10) |
| `family_income` | float | Annual family income (currency units) |
| `parental_education_level` | int | Parents' education level (0=none → 5=postgrad) |
| `internet_quality` | float | Internet quality score (1–10) |
| `library_visits` | float | Library visits per week |
| `online_courses_completed` | int | Number of online courses completed |
| `part_time_hours` | float | Weekly hours in part-time work |
| `peer_study_group` | int | Participates in study group (0=No, 1=Yes) |
| `relationship_status` | int | In a relationship (0=No, 1=Yes) |
| `hostel_student` | int | Lives in hostel/dorm (0=No, 1=Yes) |
| `extracurricular_hours` | float | Weekly extracurricular activity hours |
| `phone_unlocks_per_day` | float | Number of phone unlocks per day |
| `previous_gpa` | float | GPA from previous semester (0–10) |
| `class_participation` | float | Class participation score (1–10) |
| `weekly_study_sessions` | float | Number of dedicated study sessions per week |
| `group_study_hours` | float | Weekly hours studying in groups |
| `financial_stress` | float | Financial stress level (1–10) |
| `gpa` | float | Current GPA (0–10 scale) |
| `performance_level` | str | Academic performance category (Low / Medium / High) |

---

## 4. Data Quality

Findings from the silver layer processing (`data/silver/students_silver_report.txt`):

| Issue | Detail | Resolution |
|-------|--------|------------|
| **Missing values** | 1,558 rows had `performance_level = null` after load | Imputed as `"unknown"` (categorical fallback) |
| **Duplicates** | None detected across 1,000,000 rows | — |
| **Column naming** | Original columns used mixed case and spaces | Standardised to `snake_case` |
| **Type consistency** | All numeric columns already float/int | No conversion needed |
| **GPA range** | Min = 0.0, Max = 2.009 (not 0–10 scale as described) | Kept as-is; scale appears to be 0–2 |
| **Anxiety/Depression** | Scored 0–100 while other psych scores use 1–10 | Different scale noted; kept as-is |

> The 1,558 `unknown` performance rows show clear signals of poor performance: avg GPA of 0.0, 48.6% attendance, and 7.56 procrastination score — likely data entry gaps for the lowest-performing students.

---

## 5. Business Questions (Gold Layer)

Full results in [`data/gold/business_report_gold.txt`](data/gold/business_report_gold.txt).

**Q1 — Average GPA by Performance Level**
Low-performance students average GPA 0.83 with 64.9 final score. The `unknown` group (1,558 students) shows GPA 0.0, confirming they are extreme outliers.

**Q2 — Lifestyle Impact on GPA**
Low performers average 3.21 stress and 6.50 sleep hours vs `unknown` group with 5.05 stress and only 5.76 sleep — higher stress and less sleep correlate with worse outcomes.

**Q3 — Academic Habits by Performance**
Low performers study 4.05h/day with 74.9% attendance; `unknown` group only 0.42h/day with 48.6% attendance and 7.56 procrastination score.

**Q4 — Financial Background vs GPA**
Income group has minimal impact on GPA. Parental education level is the stronger predictor: level 0 → avg GPA 0.68; level 5 → avg GPA 0.98 across all income groups.

**Q5 — Top 10% vs Bottom 10% Profile**

| Metric | Top 10% | Bottom 10% |
|--------|---------|------------|
| Avg GPA | 1.35 | 0.32 |
| Study hours/day | 7.33 | 1.11 |
| Attendance | 93.2% | 56.3% |
| Procrastination | 3.33 | 6.65 |
| Motivation | 7.09 | 4.89 |

---

## 6. Execution Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL running locally on port 5432
- Database named `students` already created
- Kaggle account with API token

### Setup

```bash
# Clone the repo
git clone https://github.com/daniely-luz/Lab01_PART1_13775103
cd Lab01_PART1_13775103

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install 'kagglehub[pandas-datasets]' pandas sqlalchemy psycopg2-binary \
            python-dotenv pyarrow matplotlib
```

### Configure credentials

Create a `.env` file in the project root:

```
KAGGLE_API_TOKEN=your_kaggle_token_here
```

### Run in order

```bash
# 1. Raw layer — download from Kaggle and insert into PostgreSQL
python data/raw/ingestion_raw.py

# 2. Silver layer — clean data and save Parquet
python data/silver/ingestion_silver.py

# 3. Silver report — null counts, types, statistics
python data/silver/report_silver.py

# 4. Silver charts — generate 5 analysis charts + markdown
python data/silver/chart_silver.py

# 5. Gold layer — build Star Schema in PostgreSQL
python data/gold/ingestion_gold.py

# 6. Gold report — answer 5 business questions
python data/gold/report_gold.py
```
