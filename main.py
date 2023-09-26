from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import crud, database, models, schemas, aggregation
from news_api import request_articles
from processing import labelize, pre_process
from math import ceil

MAX_NUMBER_OF_PAGES_TO_FETCH = 50
TOPIC_SEARCHED = "artificial intelligence"
SOURCES_LANGUAGE = "en"
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
    initial_response = request_articles.fetch_news_articles_based_on_query(
        query=TOPIC_SEARCHED, language=SOURCES_LANGUAGE, page=1
    )
    if initial_response["status"] == "error":
        return {
            "status": initial_response["status"],
            "msg": initial_response["message"],
        }
    else:
        _, nbrArticles, articles = initial_response.values()
        nb_pages_to_query = ceil(nbrArticles / 100)
        print(f"{nb_pages_to_query} pages to query")
        print(f"{nbrArticles} expected...")
        print(f"{len(articles)} articles are going to be processed...")
        for p in range(2, nb_pages_to_query + 1):
            response = request_articles.fetch_news_articles_based_on_query(
                query=TOPIC_SEARCHED, language=SOURCES_LANGUAGE, page=p
            )
            if response["status"] == "ok":
                articles += response["articles"]
            print(f"Added {len(response['articles'])} articles to be processed")
        # selection and cleaning of articles metadata
        pre_processed_articles = pre_process.select_and_prepare_articles(articles)
        # Verify if articles already exists in db
        batched_articles = []
        for article in pre_processed_articles:
            if crud.get_article_by_id(db, article["article_id"]) is None:
                batched_articles.append(article)
        # Labelize metadata from articles into fake / real
        print(f"\nNum of articles sent for labelization is {len(batched_articles)}\n")
        enriched_articles = labelize.labelize_articles(batched_articles)
        print(f"\nNum of synced articles is {len(enriched_articles)}\n")
        return crud.batch_create_articles(db, enriched_articles)


@app.get(path="/articles/", response_model=list[schemas.NewsArticle])
async def get_available_articles(
    db: Session = Depends(get_db), source: str = "techcrunch", limit: int = 10
):
    return crud.get_all_articles(db, limit=limit)


@app.get(path="/articles/get-distribution-fake-real-per-source")
async def get_distribution_fake_real_per_source(db: Session = Depends(get_db)):
    return aggregation.aggregate_per_sources(db)


# TODO : Endpoint for calculating average confidence per label per source
