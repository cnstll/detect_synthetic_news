from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import crud, database, models, schemas
from processing import process_news

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(path="/sync_articles/", response_model=list[schemas.NewsArticle])
async def sync_news_articles(db: Session = Depends(get_db)):
    # Get news from last day
    # Create articles
    print("Starting sync...")
    news_articles = process_news.request_and_process_news()
    if not isinstance(news_articles, list):
        # TODO : How should I handle errors here ?
        raise HTTPException(
            status_code=news_articles["code"], detail=news_articles["message"]
        )
    print("BATCHED ARTICLES: ", news_articles[0])
    # Verify if article already exists
    batched_articles = []
    for article in news_articles:
        if crud.get_article_by_id(db, article["article_id"]) is None:
            batched_articles.append(article)
    print(f"\nNum of sync articles is {len(batched_articles)}\n")
    return crud.batch_create_articles(db, batched_articles)


@app.get(path="/articles", response_model=list[schemas.NewsArticle])
async def get_all_available_articles(db: Session = Depends(get_db)):
    return crud.get_all_articles(db, limit=100)
