from transformers import pipeline
import pandas as pd
import re
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


def enrich_article(article: dict, pipe) -> dict:
    """Clean data form an article and feed it to the detection model

    Args:
        article (dict): a json with the data related to an article
        pipe (_type_): instance of the detector model

    Returns:
        dict: article data enriched with a fake / real label and a confidence score
    """
    article_source = article.get("source").get("name")
    article_title = article.get("title")
    article_description = article.get("description")
    article_content = article.get("content")
    article_publish_date = article.get("publishedAt")

    # Initialize variables with default values
    title_detection = ["", 0.0]
    description_detection = ["", 0.0]
    content_detection = ["", 0.0]
    article_title = clean_article_metadata(article_title)
    article_description = clean_article_metadata(article_description)
    article_content = clean_article_metadata(article_content)

    # Transform date format from ISO 8601 to sqlalchemy compatible format
    article_publish_date = datetime.strptime(article_publish_date, "%Y-%m-%dT%H:%M:%SZ")

    # Feed article metadata to the Detector
    title_detection = pipe(article_title)[0]
    description_detection = pipe(article_description)[0]
    content_detection = pipe(article_content)[0]

    id = f"{article_publish_date} | {article_source} | {article_title}"
    m = hashlib.sha256(id.encode("UTF-8"))
    article_id = m.hexdigest()
    return {
        "article_id": article_id,
        "article_source": article_source,
        "article_publication_date": article_publish_date,
        "article_url": article.get("url"),
        "article_title": article_title,
        "title_detection_label": title_detection["label"],
        "title_detection_score": title_detection["score"],
        "article_description": article_description,
        "description_detection_label": description_detection["label"],
        "description_detection_score": description_detection["score"],
        "article_content": article_content,
        "content_detection_label": content_detection["label"],
        "content_detection_score": content_detection["score"],
    }


def process_articles(articles: list[dict]) -> list[dict]:
    """Go through a batch of articles, select and labelize them as fake / real

    Args:
        articles (list[dict]): batch of articles data in a json format

    Returns:
        list[dict]: skimmed and enriched bacth of articles
    """
    enriched_articles = []
    # LLM Detector pipeline
    pipe = pipeline("text-classification", model="roberta-base-openai-detector")
    for article in articles:
        if article_data_is_complete(article):
            enriched_article = enrich_article(article, pipe)
            enriched_articles.append(enriched_article)
    return enriched_articles


# Load model directly
# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# tokenizer = AutoTokenizer.from_pretrained("roberta-base-openai-detector")
# model = AutoModelForSequenceClassification.from_pretrained("roberta-base-openai-detector")
