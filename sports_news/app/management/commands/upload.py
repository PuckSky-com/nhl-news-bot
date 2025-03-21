from django.core.management.base import BaseCommand
from app.utils.bluesky_post import upload_content, is_youtube_url
from app.utils.llama import send_request
from news.models import Article
from highlights.models import Video
import datetime


class Command(BaseCommand):
    help = "Uploads new articles and videos from the database to Bluesky with external embed support"

    def handle(self, *args, **kwargs):
        new_articles = Article.objects.filter(is_new=True)
        new_videos = Video.objects.filter(is_new=True)

        if not new_articles.exists() and not new_videos.exists():
            self.stdout.write(self.style.ERROR("No new articles or videos to upload."))
            return

        # Process Articles
        for article in new_articles:
            self.upload_article(article)

        # Process Videos
        for video in new_videos:
            self.upload_video(video)

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
                description=video.description if hasattr(video, 'description') else "",
                img_url=video.img_url  # Ensure thumbnail is displayed
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
