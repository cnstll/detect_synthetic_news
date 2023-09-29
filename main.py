from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import crud, database, models, schemas, aggregation
from news_api import request_articles
from processing import labelize, pre_process
from math import ceil
from datetime import datetime, timedelta

MAX_NUMBER_OF_PAGES_TO_FETCH = 50
TOPIC_SEARCHED = [
    "artificial intelligence",
    "deep learning",
    "chatGPT",
    "climate change",
]
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


@app.get(path="/sync-articles")
async def sync_articles_from_query(db: Session = Depends(get_db)):
    enriched_articles = []
    for keywords in TOPIC_SEARCHED:
        initial_response = request_articles.fetch_news_articles_based_on_query(
            query=keywords, language=SOURCES_LANGUAGE, page=1
        )
        pages_per_request = 100
        if initial_response["status"] == "error":
            return {
                "status": initial_response["status"],
                "msg": initial_response["message"],
            }
        print(f"Request status : {initial_response['status']}")
        _, nbrArticles, articles = initial_response.values()
        nb_pages_to_query = ceil(nbrArticles / pages_per_request)
        print(f"{nb_pages_to_query} pages to query")
        print(f"{nbrArticles} expected...")
        print(f"{len(articles)} articles are going to be processed...")
        for p in range(2, nb_pages_to_query + 1):
            response = request_articles.fetch_news_articles_based_on_query(
                query=keywords, language=SOURCES_LANGUAGE, page=p
            )
            if response["status"] == "ok":
                articles += response["articles"]
            print(f"Added {len(response['articles'])} articles to be processed")
        # selection and cleaning of articles metadata
        pre_processed_articles = pre_process.select_and_prepare_articles(
            keywords, articles
        )
        # Verify if articles already exists in db
        batched_articles = []
        for article in pre_processed_articles:
            if crud.get_article_by_id(db, article["article_id"]) is None:
                batched_articles.append(article)
        # Labelize metadata from articles into fake / real
        print(f"\nNum of articles sent for labelization is {len(batched_articles)}\n")
        enriched_articles += labelize.labelize_articles(batched_articles)
    print(f"\nNum of synced articles is {len(enriched_articles)}\n")
    return crud.batch_create_articles(db, enriched_articles)


@app.get(path="/articles/", response_model=list[schemas.NewsArticle])
async def get_available_articles(
    db: Session = Depends(get_db),
    source: str = "techcrunch",
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 100,
):
    if from_date is not None and to_date is not None:
        print(f"Getting data between {from_date} and {to_date}")
        return crud.get_article_within_date_range(
            db, from_date=from_date, to_date=to_date, limit=limit
        )
    elif from_date is None and to_date is None:
        return crud.get_all_articles(db, limit=limit)
    else:
        # TODO : How should I handle errors with fastapi ? raise ?
        return {"status": 403, "msg": "Bad request"}


@app.get(path="/articles/get-distribution-fake-real-per-source")
async def get_distribution_fake_real_per_source(
    db: Session = Depends(get_db),
    from_date: str | None = None,
    to_date: str | None = None,
):
    if from_date is not None and to_date is not None:
        return aggregation.aggregate_per_sources(
            db, from_date=from_date, to_date=to_date
        )
    elif from_date is None and to_date is None:
        date_today = datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
        month_to_date = (datetime.today() - timedelta(days=30)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        return aggregation.aggregate_per_sources(
            db, from_date=month_to_date, to_date=date_today
        )
    else:
        return {"status": 403, "msg": "Bad request"}


# TODO : Endpoint for calculating average confidence per label per source
