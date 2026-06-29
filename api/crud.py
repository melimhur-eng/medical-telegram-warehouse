from collections import Counter
import re

from sqlalchemy import text


def get_top_products(db, limit=10):

    query = text("""
        SELECT message_text
        FROM raw.fct_messages
        WHERE message_text IS NOT NULL
    """)

    rows = db.execute(query).fetchall()

    # Common words to ignore
    stop_words = {
        "the", "and", "for", "with", "from", "this", "that", "these",
        "those", "your", "our", "their", "you", "can", "will", "only",
        "are", "was", "were", "have", "has", "had", "been", "being",
        "best", "find", "meds", "medical", "medicine", "consultation",
        "delivery", "deliveries", "service", "services", "price",
        "displayed", "violated", "urgent", "customers", "customer",
        "website", "call", "center", "today", "tonight",
        "www", "http", "https", "org", "com", "telegram", "channel",
        "che", "med", "chemed", "chemeds",
        "dear", "notice", "information", "products", "product",
        "available", "currently", "book", "starting", "startingfrom",
        "supports", "supplement", "supplements",
    }

    # Days and months
    stop_words.update({
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may",
        "june", "july", "august", "september",
        "october", "november", "december",
        "jan", "feb", "mar", "apr", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    })

    # Medical products / medicines
    medical_terms = {
        "paracetamol",
        "ibuprofen",
        "diclofenac",
        "dicloran",
        "metformin",
        "omeprazole",
        "ceftriaxone",
        "metronidazole",
        "ciprofloxacin",
        "doxycycline",
        "doxy",
        "amoxy",
        "amoxicillin",
        "ampicillin",
        "azithromycin",
        "sildenafil",
        "warfarin",
        "losartan",
        "aspirin",
        "glimepiride",
        "amlodipine",
        "bisoprolol",
        "lidocaine",
        "albendazole",
        "miconazole",
        "acyclovir",
        "salbutamol",
        "iron",
        "vitamin",
        "zinc",
        "cream",
        "syrup",
        "tablet",
        "tablets",
        "capsule",
        "capsules",
        "caps",
        "inj",
        "injection",
        "glove",
        "gloves",
        "gauze",
        "bandage",
        "syringe",
        "sanitizer",
        "oximeter",
        "microscope",
        "stethoscope",
        "thermometer"
    }

    counts = Counter()

    for row in rows:

        text_value = row[0].lower()

        # Extract English words only
        tokens = re.findall(r"[a-zA-Z][a-zA-Z\-]+", text_value)

        for token in tokens:

            token = token.strip("-")

            if len(token) < 3:
                continue

            if token in stop_words:
                continue

            if token in medical_terms:
                counts[token] += 1

    return [
        {
            "product": product,
            "mentions": mentions
        }
        for product, mentions in counts.most_common(limit)
    ]

from sqlalchemy import text


def get_channel_activity(db, channel_name):

    query = text("""
        SELECT

            channel_name,
            total_posts,
            avg_views,
            first_post_date,
            last_post_date
        FROM raw.dim_channels
        WHERE LOWER(channel_name)=LOWER(:channel_name)
    """)

    result = db.execute(
        query,
        {
            "channel_name": channel_name
        }
    ).fetchone()

    if result is None:
        return None
    return {

        "channel_name": result.channel_name,
        "total_posts": result.total_posts,
        "avg_views": float(result.avg_views),
        "first_post_date": str(result.first_post_date),
        "last_post_date": str(result.last_post_date)

    }
def search_messages(
    db,
    query_text,
    limit=20
):

    sql = text("""
        SELECT
            message_id,
            message_text,
            views,
            forwards,
            channel_key,
            date_key
        FROM raw.fct_messages
        WHERE LOWER(message_text)
        LIKE LOWER(:search)
        LIMIT :limit
    """)

    rows = db.execute(
        sql,

        {
            "search": f"%{query_text}%",
            "limit": limit
        }

    )
    return [
        dict(row._mapping)
        for row in rows
    ]

def visual_content_stats(db):

    sql = text("""
        SELECT
            c.channel_name,
            d.image_category,
            COUNT(*) AS total
        FROM raw.fct_image_detections d
        JOIN raw.dim_channels c
            ON d.channel_key = c.channel_key
        GROUP BY
            c.channel_name,
            d.image_category
        ORDER BY
            c.channel_name
    """)

    rows = db.execute(sql).fetchall()

    stats = {}

    for row in rows:
        channel = row.channel_name
        category = row.image_category
        count = row.total

        if channel not in stats:

            stats[channel] = {
                "channel_name": channel,
                "promotional": 0,
                "product_display": 0,
                "lifestyle": 0,
                "other": 0
            }

        if category in stats[channel]:
            
            stats[channel][category] = count

    return list(stats.values())