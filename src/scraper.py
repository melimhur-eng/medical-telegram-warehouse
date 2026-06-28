
import os
import json
import asyncio
from datetime import datetime

from telegram_client import client
from config import RAW_DATA_DIR, IMAGE_DIR
from utils import logger

# --------------------------------------------------------------------
# Telegram channels
# --------------------------------------------------------------------

CHANNELS = [
    "CheMed123",
    "lobelia4cosmetics",
    "tikvahpharma",
]

# --------------------------------------------------------------------
# Create required directories
# --------------------------------------------------------------------

today = datetime.now().strftime("%Y-%m-%d")

os.makedirs(os.path.join(RAW_DATA_DIR, today), exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)


# --------------------------------------------------------------------
# Scrape a single channel
# --------------------------------------------------------------------

async def scrape_channel(channel_name: str):

    logger.info(f"Started scraping {channel_name}")

    messages = []

    image_directory = os.path.join(IMAGE_DIR, channel_name)
    os.makedirs(image_directory, exist_ok=True)

    async for message in client.iter_messages(channel_name):

        image_path = None

        # ----------------------------------------------------------
        # Download image if present
        # ----------------------------------------------------------

        if message.photo:

            image_path = os.path.join(
                image_directory,
                f"{message.id}.jpg"
            )

            try:
                await client.download_media(
                    message,
                    file=image_path
                )

            except Exception as e:
                logger.error(
                    f"Image download failed "
                    f"{channel_name}/{message.id}: {e}"
                )

        # ----------------------------------------------------------
        # Message dictionary
        # ----------------------------------------------------------

        message_data = {

            "message_id": message.id,

            "channel_name": channel_name,

            "date": (
                message.date.isoformat()
                if message.date else None
            ),

            "text": message.message,

            "views": message.views,

            "forwards": message.forwards,

            "has_media": message.media is not None,

            "media_type": (
                type(message.media).__name__
                if message.media
                else None
            ),

            "image_path": image_path

        }

        messages.append(message_data)

    logger.info(
        f"{channel_name}: {len(messages)} messages collected."
    )

    return messages


# --------------------------------------------------------------------
# Save JSON
# --------------------------------------------------------------------

def save_messages(channel_name, messages):

    filename = os.path.join(
        RAW_DATA_DIR,
        today,
        f"{channel_name}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=4
        )

    logger.info(f"Saved {filename}")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

async def main():

    logger.info("=" * 60)
    logger.info("Telegram scraping started")

    await client.start()

    for channel in CHANNELS:

        try:

            messages = await scrape_channel(channel)

            save_messages(
                channel,
                messages
            )

        except Exception as e:

            logger.exception(
                f"Failed scraping {channel}: {e}"
            )

    await client.disconnect()

    logger.info("Scraping completed.")
    logger.info("=" * 60)


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())