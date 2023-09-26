from transformers import pipeline
import hashlib
from datetime import datetime


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


def labelize_articles(articles: list[dict]) -> list[dict]:
    """Go through a batch of articles, labelize article as fake / real

    Args:
        articles (list[dict]): batch of articles data in a json format

    Returns:
        list[dict]: list of labelized articles metadata
    """
    labelized_articles = []
    # LLM Detector pipeline
    pipe = pipeline("text-classification", model="roberta-base-openai-detector")
    for article in articles:
        enriched_article = enrich_article(article, pipe)
        labelized_articles.append(enriched_article)
    return labelized_articles


# Load model directly
# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# tokenizer = AutoTokenizer.from_pretrained("roberta-base-openai-detector")
# model = AutoModelForSequenceClassification.from_pretrained("roberta-base-openai-detector")
