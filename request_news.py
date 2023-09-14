from transformers import pipeline
import pandas as pd
import requests
import re
import json
import os
from dotenv import load_dotenv

load_dotenv()


## HELPER FUNCTIONS
def value_was_removed(value: str) -> bool:
    return value.find("Removed") > 0


def value_has_none_string(value: str) -> bool:
    return value.find("None") > 0


def clean_text(text: str) -> str:
    chars_counter_pattern = r"\[\+\d+ chars\]"
    cleaned_text = re.sub(chars_counter_pattern, "", text)
    return cleaned_text.replace("\r\n", "")


## END HELPER FUNCTIONS

# Call To the News API
request_country = "us&"
request_source = "bbc-news&"
api_key = os.getenv("NEWS_API_KEY")
url = (
    "https://newsapi.org/v2/top-headlines?"
    f"country={request_country}"
    f"apiKey={api_key}"
)
# response = requests.get(url)
# status, count, articles =  response.json()

# Load articles dict from file to save on api calls
# with open("api_like_responses_generated_by_gpt.json", "r") as user_file:
with open("api_response_top_headlines.json", "r") as user_file:
    response = user_file.read()
parsed_json = json.loads(response)

status, count, articles = parsed_json.values()


if status == "ok":
    pipe = pipeline("text-classification", model="roberta-base-openai-detector")
    cleaned_url = url.replace(api_key, "XXX")
    results = []
    for article in articles:
        article_source = article.get("source").get("name")
        if not value_was_removed(article_source):
            article_title = article.get("title")
            article_description = article.get("description")
            article_content = article.get("content")
            if (
                article_title is None
                or article_description is None
                or article_content is None
            ):
                continue

            # Initialize variables with default values
            title_detection = ["", 0.0]
            description_detection = ["", 0.0]
            content_detection = ["", 0.0]

            # Check for None str values in each article field before getting through the detector
            if not value_has_none_string(article_title):
                article_title = clean_text(article_title)
                title_detection = pipe(article_title)[0]
            if not value_has_none_string(article_description):
                article_description = clean_text(article_description)
                description_detection = pipe(article_description)[0]
            if not value_has_none_string(article_content):
                article_content = clean_text(article_content)
                content_detection = pipe(article_content)[0]

            results.append(
                {
                    "request_url": cleaned_url,
                    "article_source": article_source,
                    "article_publication_date": article.get("publishedAt"),
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
            )
# Store results of the analysis in a dataframe

column_names = [
    "request_url",
    "article_source",
    "article_url",
    "article_publication_date",
    "article_title",
    "title_detection_label",
    "title_detection_score",
    "article_description",
    "description_detection_label",
    "description_detection_score",
    "article_content",
    "content_detection_label",
    "content_detection_score",
]
df_detection_results = pd.DataFrame(results, columns=column_names)
print(df_detection_results["title_detection_label"].value_counts())
print(df_detection_results["description_detection_label"].value_counts())
print(df_detection_results["content_detection_label"].value_counts())
df_detection_results.to_csv("results.csv")
# Load model directly
# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# tokenizer = AutoTokenizer.from_pretrained("roberta-base-openai-detector")
# model = AutoModelForSequenceClassification.from_pretrained("roberta-base-openai-detector")
