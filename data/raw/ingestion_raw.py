# Install dependencies as needed:
# pip install kagglehub[pandas-datasets] python-dotenv psycopg2-binary sqlalchemy
import os
from dotenv import load_dotenv
import kagglehub
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

# Download dataset to local cache
path = kagglehub.dataset_download("sharmajicoder/college-students-habits-and-performance")
print("Downloaded to:", path)
print("Files:", os.listdir(path))

# Load the CSV
csv_file = os.path.join(path, os.listdir(path)[0])
df = pd.read_csv(csv_file)
print(f"Loaded {len(df)} rows")
print("First 5 records:", df.head())

# Insert into PostgreSQL
url = URL.create(
    drivername="postgresql+psycopg2",
    username="daniely.santos",
    host="localhost",
    port=5432,
    database="students",
)
engine = create_engine(url)

df.to_sql("students", engine, if_exists="replace", index=False)
print("Data inserted into 'students' table successfully.")