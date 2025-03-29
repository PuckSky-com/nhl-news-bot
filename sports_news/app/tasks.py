from celery import shared_task
from app.utils.bluesky_post import upload_content
from news.models import Article
from highlights.models import Video
import datetime

@shared_task
def upload_to_bluesky():
    articles = Article.objects.filter(is_new=True)
    videos = Video.objects.filter(is_new=True)

    for article in articles:
        upload_content(
            text=article.title,
            title=article.title,
            link=article.link,
            description=article.description,
            img_url=article.img_url
        )
        article.is_new = False
        article.save()

    for video in videos:
        upload_content(
            text=video.title,
            title=video.title,
            link=video.embed_url,
            description="",
            img_url=video.img_url
        )
        video.is_new = False
        video.save()

    return f"Uploaded {articles.count()} articles and {videos.count()} videos."
