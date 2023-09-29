from transformers import pipeline
import re
from datetime import datetime
import hashlib
from datetime import datetime


def value_was_removed(value: str) -> bool:
    return value.find("Removed") > 0


def value_has_none_string(value: str) -> bool:
    return value.find("None") > 0


def clean_article_metadata(text: str) -> str:
    chars_counter_pattern = r"\[\+\d+ chars\]"
    cleaned_text = re.sub(chars_counter_pattern, "", text)
    return cleaned_text.replace("\r\n", "")


def generate_article_id(source: str, title: str, publish_date: str) -> str:
    ingestion_date = datetime.today()
    id = f"{ingestion_date}|{publish_date}|{source}|{title}"
    m = hashlib.sha256(id.encode("UTF-8"))
    return m.hexdigest()


def article_data_is_complete(article: dict) -> bool:
    """Check for missing values or incomplete metadata in articles extracted from the news api

    Args:
        article (dict): a json with the data related to an article

    Returns:
        bool: if no none value or str true will be returned, else false
    """
    # If removed field do not retain article
    if value_was_removed(article.get("source").get("name")):
        return None
    # If Missing field and None string do not retain article
    if any(
        list(
            map(
                lambda x: x is None or value_has_none_string(x),
                [
                    article.get("title"),
                    article.get("description"),
                    article.get("content"),
                    article.get("publishedAt"),
                ],
            )
        )
    ):
        return False
    else:
        return True


def prepare_metadata(searched_keywords: str, article: dict) -> dict:
    """Extract pieces of metadata from the article info

    Args:
        article (dict): article object from the news api

    Returns:
        dict: transformed article metadata
    """
    article_source = article.get("source").get("name")
    article_publication_date = article.get("publishedAt")
    article_title = clean_article_metadata(article.get("title"))
    article_description = clean_article_metadata(article.get("description"))
    article_content = clean_article_metadata(article.get("content"))
    article_url = article.get("url")
    # Generate a unique id to store the article into the DB
    article_id = generate_article_id(
        article_source,
        article_title,
        article_publication_date,
    )
    # Transform date format from ISO 8601 to sqlalchemy compatible format
    article_publication_date = datetime.strptime(
        article.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ"
    )

    return {
        "article_id": article_id,
        "article_source": article_source,
        "article_publication_date": article_publication_date,
        "article_url": article_url,
        "article_title": article_title,
        "article_description": article_description,
        "article_content": article_content,
        "searched_keywords": searched_keywords,
    }


def select_and_prepare_articles(
    searched_keywords: str, articles: list[dict]
) -> list[dict]:
    """Go through a batch of articles, remove articles with uncomplete data and clean metadata
    Args:
        articles (list[dict]): batch of articles data in a json format

    Returns:
        list[dict]: skimmed  batch of articles
    """
    selected_articles = []
    for article in articles:
        if article_data_is_complete(article):
            article_metadata = prepare_metadata(searched_keywords, article)
            selected_articles.append(article_metadata)
    return selected_articles
