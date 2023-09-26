from transformers import pipeline


def enrich_article(article: dict, pipe) -> dict:
    """Clean data form an article and feed it to the detection model

    Args:
        article (dict): a json with the data related to an article
        pipe (_type_): instance of the detector model

    Returns:
        dict: article data enriched with a fake / real label and a confidence score
    """
    article_title = article.get("article_title")
    article_description = article.get("article_description")
    article_content = article.get("article_content")

    # Initialize variables with default values
    title_detection = ["", 0.0]
    description_detection = ["", 0.0]
    content_detection = ["", 0.0]

    # Feed article metadata to the Detector
    title_detection = pipe(article_title)[0]
    description_detection = pipe(article_description)[0]
    content_detection = pipe(article_content)[0]

    return {
        "title_detection_label": title_detection["label"],
        "title_detection_score": title_detection["score"],
        "description_detection_label": description_detection["label"],
        "description_detection_score": description_detection["score"],
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
        enriched_metadata = enrich_article(article, pipe)
        article.update(enriched_metadata)
        labelized_articles.append(article)
    return labelized_articles


# Load model directly
# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# tokenizer = AutoTokenizer.from_pretrained("roberta-base-openai-detector")
# model = AutoModelForSequenceClassification.from_pretrained("roberta-base-openai-detector")
