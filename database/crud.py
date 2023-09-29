from sqlalchemy.orm import Session
from . import models, schemas


# Create
def create_article(db: Session, article_data: schemas.NewsArticle):
    article = models.NewsArticle(**article_data.dict())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def batch_create_articles(db: Session, articles_data: list[schemas.NewsArticle]):
    batched_articles = [models.NewsArticle(**article) for article in articles_data]
    db.add_all(batched_articles)
    db.commit()
    for article in batched_articles:
        db.refresh(article)
    return batched_articles


# Read (Get by ID)
def get_article_by_id(db: Session, article_id: str):
    return (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.article_id == article_id)
        .first()
    )


# Read (Get by Source)
def get_article_by_source(db: Session, article_source: str):
    return (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.article_source == article_source)
        .first()
    )


# Read (Get by date)
def get_article_by_publication_date(db: Session, article_publication_date: str):
    return (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.article_publication_date == article_publication_date)
        .first()
    )


def get_article_within_date_range(
    db: Session, from_date: str, to_date: str, limit: int = 100
):
    return (
        db.query(models.NewsArticle)
        .filter(
            models.NewsArticle.article_publication_date >= from_date,
            models.NewsArticle.article_publication_date <= to_date,
        )
        .limit(limit)
        .all()
    )


# Read (Get all articles)
def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.NewsArticle).offset(skip).limit(limit).all()


# Update
def update_article(db: Session, article_id: str, article_data: schemas.NewsArticle):
    article = (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.article_id == article_id)
        .first()
    )
    if article:
        for key, value in article_data.dict().items():
            setattr(article, key, value)
        db.commit()
        db.refresh(article)
    return article


# Delete
def delete_article(db: Session, article_id: str):
    article = (
        db.query(models.NewsArticle)
        .filter(models.NewsArticle.article_id == article_id)
        .first()
    )
    if article:
        db.delete(article)
        db.commit()
        return True
    return False
