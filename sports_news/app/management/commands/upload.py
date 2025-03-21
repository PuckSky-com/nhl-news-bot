from django.core.management.base import BaseCommand
from app.utils.bluesky_post import upload_content, is_youtube_url
from django.db import transaction
from app.utils.llama import send_request
from news.models import Article
from highlights.models import Video
import datetime


class Command(BaseCommand):
    help = "Uploads new articles and videos from the database to Bluesky with external embed support"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            new_articles = list(Article.objects.filter(is_new=True).select_for_update())
            new_videos = list(Video.objects.filter(is_new=True).select_for_update())

            # Mark items as processing to prevent duplicates
            for article in new_articles:
                article.is_new = False
                article.save()
                
            for video in new_videos:
                video.is_new = False
                video.save()

    def upload_article(self, article: Article):
        """Uploads an article to Bluesky"""
        try:
            text = send_request(article.title, article.description)
            upload_content(
                text=text if text else article.title,
                title=article.title,
                link=article.link,
                description=article.description,
                img_url=article.img_url
            )
            article.is_new = False
            article.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully uploaded article: {article.title} at {datetime.datetime.now()}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error uploading article '{article.title}': {e}")
            )

    def upload_video(self, video: Video):
        try:
            video_id = is_youtube_url(video.embed_url)

            text = send_request(video.title, video.description if hasattr(video, 'description') else "")
            
            upload_content(
                text=text if text else video.title,  # Use generated text or fallback to title
                title=video.title,
                link=f"https://www.youtube.com/watch?v={video_id}",
                description="",
                img_url=video.img_url
            )

            video.is_new = False
            video.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully uploaded video: {video.title} at {datetime.datetime.now()}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error uploading video '{video.title}': {e}")
            )
