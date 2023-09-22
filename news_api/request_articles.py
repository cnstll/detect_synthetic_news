import os
from typing import Tuple
from dotenv import load_dotenv
import requests

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
    return response.json()


def fetch_all_news_articles(
    from_date: str = "2023-09-15",
    language: str = None,
    query: str = None,
    category: str = None,
) -> Tuple[str, int, dict]:
    # Prepare request url
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?from_date={from_date}&apiKey={api_key}"
    # Specify the url request if needed
    if category is not None:
        request_category = f"category={category}"
        url += f"&{request_category}"
    if language is not None:
        request_country = f"language={language}"
        url += f"&{request_country}"
    if query is not None:
        request_query = f"q={query}"
        url += f"&{request_query}"

    # API Call
    response = requests.get(url)
    return response.json()
