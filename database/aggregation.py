from sqlalchemy import func, case
from sqlalchemy.orm import Session
from . import models, schemas


# Query summing and averaging article metadata labels and confidence scores per source
def aggregate_per_sources(db: Session):
    result = (
        db.query(
            models.NewsArticle.article_source,
            func.sum(
                case([(models.NewsArticle.title_detection_label == "Fake", 1)], else_=0)
            ).label("sum_of_fake_titles"),
            func.sum(
                case([(models.NewsArticle.title_detection_label == "Real", 1)], else_=0)
            ).label("sum_of_real_titles"),
            func.sum(
                case(
                    [(models.NewsArticle.description_detection_label == "Fake", 1)],
                    else_=0,
                )
            ).label("sum_of_fake_descriptions"),
            func.sum(
                case(
                    [(models.NewsArticle.description_detection_label == "Real", 1)],
                    else_=0,
                )
            ).label("sum_of_real_descriptions"),
            func.sum(
                case(
                    [(models.NewsArticle.content_detection_label == "Fake", 1)], else_=0
                )
            ).label("sum_of_fake_contents"),
            func.sum(
                case(
                    [(models.NewsArticle.content_detection_label == "Real", 1)], else_=0
                )
            ).label("sum_of_real_contents"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.title_detection_label == "Fake",
                            models.NewsArticle.title_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_fake_titles"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.title_detection_label == "Real",
                            models.NewsArticle.title_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_real_titles"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.description_detection_label == "Fake",
                            models.NewsArticle.description_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_fake_descriptions"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.description_detection_label == "Real",
                            models.NewsArticle.description_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_real_descriptions"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.content_detection_label == "Fake",
                            models.NewsArticle.content_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_fake_contents"),
            func.avg(
                case(
                    [
                        (
                            models.NewsArticle.content_detection_label == "Real",
                            models.NewsArticle.content_detection_score,
                        )
                    ],
                    else_=None,
                )
            ).label("average_score_for_real_contents"),
        )
        .group_by(models.NewsArticle.article_source)
        .all()
    )
    return result
