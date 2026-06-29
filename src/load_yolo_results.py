import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


# Load .env from project root (one level above src)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print(f"Loading environment from: {ENV_PATH}")

if not ENV_PATH.exists():
    raise FileNotFoundError(f".env file not found at {ENV_PATH}")

load_dotenv(ENV_PATH)


# Read database credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")



# Create PostgreSQL connection
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Load YOLO results
csv_path = BASE_DIR / "data" / "processed" / "yolo_results.csv"

if not csv_path.exists():
    raise FileNotFoundError(
        f"YOLO results file not found: {csv_path}"
    )

df = pd.read_csv(csv_path)


# Load into PostgreSQL
df.to_sql(
    "image_detections",
    engine,
    schema="raw",
    if_exists="replace",
    index=False
)

print("YOLO results loaded successfully.")