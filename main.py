from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import crud, database, models, schemas
from news_api import request_articles
from processing import process_articles

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
    response = request_articles.fetch_top_news_articles(
        country="us", category="technology"
    )
    if response["status"] == "ok":
        _, _, articles = response.values()
        articles = process_articles.process_articles(articles)
        # Verify if article already exists in db
        batched_articles = []
        for article in articles:
            if crud.get_article_by_id(db, article["article_id"]) is None:
                batched_articles.append(article)
        print(f"\nNum of synced articles is {len(batched_articles)}\n")
        return crud.batch_create_articles(db, batched_articles)
    else:
        # TODO : How should I better handle errors here ?
        raise HTTPException(status_code=response["code"], detail=response["message"])


@app.get(path="/articles", response_model=list[schemas.NewsArticle])
async def get_all_available_articles(db: Session = Depends(get_db)):
    return crud.get_all_articles(db, limit=100)
