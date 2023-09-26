from transformers import pipeline
import re
from datetime import datetime


def value_was_removed(value: str) -> bool:
    return value.find("Removed") > 0


def value_has_none_string(value: str) -> bool:
    return value.find("None") > 0


def clean_article_metadata(text: str) -> str:
    chars_counter_pattern = r"\[\+\d+ chars\]"
    cleaned_text = re.sub(chars_counter_pattern, "", text)
    return cleaned_text.replace("\r\n", "")


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


def select_and_clean_articles(articles: list[dict]) -> list[dict]:
    """Go through a batch of articles, remove articles with uncomplete data and clean metadata
    Args:
        articles (list[dict]): batch of articles data in a json format

    Returns:
        list[dict]: skimmed  batch of articles
    """
    selected_articles = []
    for article in articles:
        if article_data_is_complete(article):
            article["title"] = clean_article_metadata(article.get(["title"]))
            article["description"] = clean_article_metadata(
                article.get(["description"])
            )
            article["content"] = clean_article_metadata(article.get(["content"]))
            selected_articles.append(article)
    return selected_articles
