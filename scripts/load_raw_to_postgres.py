"""
Load Telegram JSON files into PostgreSQL raw schema.

Usage:
    python scripts/load_raw_to_postgres.py
"""

import json
import logging
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json
from pathlib import Path

# -------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATA_DIR = Path("data/raw/telegram_messages")

# -------------------------------------------------------
# Logging
# -------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "load_raw_to_postgres.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)


# -------------------------------------------------------
# Database Connection
# -------------------------------------------------------

def get_connection():
    """Create PostgreSQL connection."""

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# -------------------------------------------------------
# Create Schema & Table
# -------------------------------------------------------

def create_raw_table(cursor):
    """Create raw schema and telegram_messages table."""

    cursor.execute(
        """
        CREATE SCHEMA IF NOT EXISTS raw;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (

            id SERIAL PRIMARY KEY,

            message_id BIGINT NOT NULL,

            channel_name TEXT,

            message_date TIMESTAMP,

            message_text TEXT,

            views INTEGER,

            forwards INTEGER,

            has_media BOOLEAN,

            image_path TEXT,

            raw_json JSONB,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(message_id, channel_name)

        );
        """
    )


# -------------------------------------------------------
# Read JSON Files
# -------------------------------------------------------

def load_json(file_path):
    """Read JSON file."""

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------------
# Insert Messages
# -------------------------------------------------------

def insert_messages(cursor, messages):

    sql = """
    INSERT INTO raw.telegram_messages (

        message_id,
        channel_name,
        message_date,
        message_text,
        views,
        forwards,
        has_media,
        image_path,
        raw_json

    )

    VALUES (

        %s,%s,%s,%s,%s,%s,%s,%s,%s

    )

    ON CONFLICT (message_id, channel_name)

    DO NOTHING;
    """

    inserted = 0

    for msg in messages:

        try:

            cursor.execute(
                sql,
                (
                    msg.get("message_id"),
                    msg.get("channel_name"),
                    msg.get("date"),
                    msg.get("text"),
                    msg.get("views"),
                    msg.get("forwards"),
                    msg.get("has_media"),
                    msg.get("image_path"),
                    Json(msg),
                ),
            )

            inserted += 1

        except Exception as e:

            logging.error(
                "Failed inserting message %s : %s",
                msg.get("message_id"),
                e,
            )

    return inserted


# -------------------------------------------------------
# Main Loader
# -------------------------------------------------------

def main():

    if not DATA_DIR.exists():

        logging.error("Directory not found: %s", DATA_DIR)

        return

    conn = None

    try:

        logging.info("Connecting to PostgreSQL...")

        conn = get_connection()

        cursor = conn.cursor()

        create_raw_table(cursor)

        conn.commit()

        logging.info("Raw schema ready.")

        total_files = 0
        total_messages = 0

        json_files = sorted(DATA_DIR.rglob("*.json"))

        if not json_files:

            logging.warning("No JSON files found.")

            return

        for json_file in json_files:

            logging.info("Reading %s", json_file)

            try:

                messages = load_json(json_file)

                if not isinstance(messages, list):

                    logging.warning(
                        "%s is not a list. Skipping.",
                        json_file,
                    )

                    continue

                inserted = insert_messages(cursor, messages)

                conn.commit()

                total_files += 1
                total_messages += inserted

                logging.info(
                    "Inserted %s messages from %s",
                    inserted,
                    json_file.name,
                )

            except json.JSONDecodeError:

                logging.error(
                    "Invalid JSON file: %s",
                    json_file,
                )

            except Exception as e:

                logging.exception(
                    "Failed processing %s : %s",
                    json_file,
                    e,
                )

        logging.info("-----------------------------------")
        logging.info("Finished Loading")
        logging.info("Files Processed : %s", total_files)
        logging.info("Messages Loaded : %s", total_messages)
        logging.info("-----------------------------------")

        cursor.close()

    except psycopg2.Error as e:

        logging.exception("Database Error: %s", e)

    finally:

        if conn:

            conn.close()

            logging.info("Database connection closed.")


# -------------------------------------------------------

if __name__ == "__main__":
    main()