from .database import Base
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint, DateTime


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String, unique=True, index=True, nullable=False)
    article_source = Column(String, nullable=False)
    article_url = Column(String, nullable=False)
    article_publication_date = Column(DateTime, nullable=False)
    article_title = Column(String, nullable=False)
    searched_keywords = Column(String, nullable=False)
    title_detection_label = Column(String, nullable=True)
    title_detection_score = Column(Float, nullable=True)
    article_description = Column(String, nullable=True)
    description_detection_label = Column(String, nullable=True)
    description_detection_score = Column(Float, nullable=True)
    article_content = Column(String, nullable=True)
    content_detection_label = Column(String, nullable=True)
    content_detection_score = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint("article_id", name="unique_article_id"),)
