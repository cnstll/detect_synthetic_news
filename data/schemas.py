from pydantic import BaseModel
from datetime import datetime


class NewsArticle(BaseModel):
    article_id: str
    article_source: str
    article_url: str
    article_publication_date: datetime
    article_title: str
    title_detection_label: str
    title_detection_score: float
    article_description: str
    description_detection_label: str
    description_detection_score: float
    article_content: str
    content_detection_label: str
    content_detection_score: float

    class Config:
        orm_mode = True
