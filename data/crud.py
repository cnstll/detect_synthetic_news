from sqlalchemy.orm import Session
from .models import NewsArticle
from .schemas import NewsArticle


# Create
def create_article(db: Session, article_data: NewsArticle):
    article = NewsArticle(**article_data.dict())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# Read (Get by ID)
def get_article_by_id(db: Session, article_id: str):
    return db.query(NewsArticle).filter(NewsArticle.article_id == article_id).first()


# Read (Get by Source)
def get_article_by_source(db: Session, article_source: str):
    return (
        db.query(NewsArticle)
        .filter(NewsArticle.article_source == article_source)
        .first()
    )


# Read (Get by date)
def get_article_by_publication_date(db: Session, article_publication_date: str):
    return (
        db.query(NewsArticle)
        .filter(NewsArticle.article_publication_date == article_publication_date)
        .first()
    )


# Read (Get all articles)
def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(NewsArticle).offset(skip).limit(limit).all()


# Update
def update_article(db: Session, article_id: str, article_data: NewsArticle):
    article = db.query(NewsArticle).filter(NewsArticle.article_id == article_id).first()
    if article:
        for key, value in article_data.dict().items():
            setattr(article, key, value)
        db.commit()
        db.refresh(article)
    return article


# Delete
def delete_article(db: Session, article_id: str):
    article = db.query(NewsArticle).filter(NewsArticle.article_id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        return True
    return False
