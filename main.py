from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import crud, database, models, schemas, aggregation
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


@app.get(path="/sync-articles")
async def sync_articles_from_query(db: Session = Depends(get_db)):
    response = request_articles.fetch_all_news_articles(
        query="artificial intelligence", language="en"
    )
    if response["status"] == "error":
        return {"status": response["status"], "msg": response["message"]}
    else:
        _, _, articles = response.values()
        articles = process_articles.process_articles(articles)
        # Verify if article already exists in db
        batched_articles = []
        for article in articles:
            if crud.get_article_by_id(db, article["article_id"]) is None:
                batched_articles.append(article)
        print(f"\nNum of synced articles is {len(batched_articles)}\n")
        return crud.batch_create_articles(db, batched_articles)


@app.get(path="/articles", response_model=list[schemas.NewsArticle])
async def get_all_available_articles(db: Session = Depends(get_db)):
    return crud.get_all_articles(db, limit=100)


# TODO : Endpoint for calculating fake / real distribution per source
@app.get(path="/articles/get-distribution-fake-real-per-source")
async def get_distribution_fake_real_per_source(db: Session = Depends(get_db)):
    return aggregation.aggregate_per_sources(db)


# TODO : Endpoint for calculating average confidence per label per source
