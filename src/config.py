import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("PHONE_NUMBER")

RAW_DATA_DIR = "data/raw/telegram_messages"
IMAGE_DIR = "data/raw/images"
LOG_DIR = "logs"