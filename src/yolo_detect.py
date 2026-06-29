from ultralytics import YOLO
from pathlib import Path
import pandas as pd

# Load model
model = YOLO("yolov8n.pt")

image_dir = Path("data/raw/images")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)


def classify_image(objects):
    """
    Classify an image according to the project requirements.
    """

    objects = set(objects)

    # YOLO labels that represent products
    product_objects = {
        "bottle",
        "cup",
        "wine glass"
    }

    has_person = "person" in objects
    has_product = len(product_objects.intersection(objects)) > 0

    if has_person and has_product:
        return "promotional"

    elif has_product:
        return "product_display"

    elif has_person:
        return "lifestyle"

    else:
        return "other"


records = []

for image in image_dir.rglob("*.jpg"):
    print(f"Processing: {image}")

    try:
        results = model(str(image))
    except Exception as e:
        print(f"Error reading {image}")
        print(e)
        continue

    channel = image.parent.name
    message_id = image.stem

    results = model(str(image), verbose=False)

    detected_objects = []

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            object_name = model.names[class_id]

            detected_objects.append(object_name)

            records.append({
                "message_id": message_id,
                "channel_name": channel,
                "detected_object": object_name,
                "confidence_score": round(confidence, 3)
            })

    # If nothing detected
    if len(detected_objects) == 0:

        records.append({
            "message_id": message_id,
            "channel_name": channel,
            "detected_object": None,
            "confidence_score": None
        })

# Convert to dataframe
df = pd.DataFrame(records)

# Determine image category
categories = []

for message_id, group in df.groupby("message_id"):

    objects = group["detected_object"].dropna().tolist()

    category = classify_image(objects)

    group = group.copy()
    group["image_category"] = category

    categories.append(group)

final_df = pd.concat(categories)

output_file = output_dir / "yolo_results.csv"

final_df.to_csv(output_file, index=False)

print(f"Saved {len(final_df)} detections.")
print(final_df.head())