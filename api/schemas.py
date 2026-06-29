from pydantic import BaseModel


class TopProduct(BaseModel):
    product: str
    mentions: int


class ChannelActivity(BaseModel):
    channel_name: str
    total_posts: int
    avg_views: float
    first_post_date: str
    last_post_date: str


class MessageSearch(BaseModel):
    message_id: int
    message_text: str
    views: int
    forwards: int
    channel_key: str
    date_key: int

class VisualContent(BaseModel):
    channel_name: str
    total_images: int
    promotional: int
    product_display: int
    lifestyle: int
    other: int

