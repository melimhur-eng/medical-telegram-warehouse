from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.crud import get_top_products, get_channel_activity,search_messages,visual_content_stats

app = FastAPI(
    title="Medical Telegram Warehouse API"
)

@app.get("/")
def root():
    return {"message": "API Running"}

@app.get("/api/reports/top-products")
def top_products(
        limit: int = 10,
        db: Session = Depends(get_db)
):
    return get_top_products(db, limit)

@app.get("/api/channels/{channel_name}")
def channel_activity(
    channel_name: str,
    db: Session = Depends(get_db)
):

    data = get_channel_activity(
        db,
        channel_name
    )

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Channel not found"
        )
    return data

@app.get("/api/search/messages")
def search(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return search_messages(
        db,
        query,
        limit
    )

@app.get("/api/reports/visual-content")
def visual_content(
    db: Session = Depends(get_db)
):

    return visual_content_stats(db)