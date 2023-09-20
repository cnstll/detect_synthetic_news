from transformers import pipeline
import pandas as pd
import requests
import re
import json
import hashlib
from datetime import datetime
import os
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()


## HELPER FUNCTIONS
def fetch_top_news_articles(
    country: str = None,
    category: str = None,
) -> Tuple[str, int, dict]:
    # Prepare request url
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/top-headlines?apiKey={api_key}"
    # Specify the url request if needed
    if category is not None:
        request_category = f"category={category}"
        url += f"&{request_category}"
    if country is not None:
        request_country = f"country={country}"
        url += f"&{request_country}"

    # API Call
    response = requests.get(url)
    print(response.json())
    return response.json()


def value_was_removed(value: str) -> bool:
    return value.find("Removed") > 0


def value_has_none_string(value: str) -> bool:
    return value.find("None") > 0


def clean_article_metadata(text: str) -> str:
    chars_counter_pattern = r"\[\+\d+ chars\]"
    cleaned_text = re.sub(chars_counter_pattern, "", text)
    return cleaned_text.replace("\r\n", "")


def process_article(article, pipe):
    article_source = article.get("source").get("name")
    # If removed field do not retain article
    if value_was_removed(article_source):
        return None

    article_title = article.get("title")
    article_description = article.get("description")
    article_content = article.get("content")
    article_publish_date = article.get("publishedAt")
    # If Missing field and None string do not retain article
    if any(
        list(
            map(
                lambda x: x is None or value_has_none_string(x),
                [
                    article_title,
                    article_description,
                    article_content,
                    article_publish_date,
                ],
            )
        )
    ):
        return None

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


## END HELPER FUNCTIONS

# Call To the News API

# Load articles dict from file to save on api calls
# with open("api_like_responses_generated_by_gpt.json", "r") as user_file:
# with open("api_response_top_headlines.json", "r") as user_file:
#    response = user_file.read()
# parsed_json = json.loads(response)

# status, count, articles = parsed_json.values()


def request_and_process_news() -> list[dict] | str:
    response = fetch_top_news_articles(country="us", category="technology")
    processing_response = []
    if response["status"] == "ok":
        _, _, articles = response.values()
        pipe = pipeline("text-classification", model="roberta-base-openai-detector")
        for article in articles:
            enrich_article = process_article(article, pipe)
            if enrich_article is not None:
                processing_response.append(enrich_article)
        return processing_response
    else:
        return response


# Load model directly
# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# tokenizer = AutoTokenizer.from_pretrained("roberta-base-openai-detector")
# model = AutoModelForSequenceClassification.from_pretrained("roberta-base-openai-detector")
