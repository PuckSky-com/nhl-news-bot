from django.core.management.base import BaseCommand
from app.utils.bluesky_post import upload_content
from app.utils.llama import send_request
from scrape.models import Article
import datetime

class Command(BaseCommand):
    help = 'Uploads new articles from the database to Bluesky with external embed support'

    def handle(self, *args, **kwargs):
        new_articles = Article.objects.filter(is_new=True)
        
        if not new_articles.exists():
            self.stdout.write(self.style.ERROR("No new articles to upload."))
            return

        for article in new_articles:
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
                    self.style.ERROR(
                        f"Error uploading article '{article.title}': {e}. Deleting article."
                    )
                )
                article.delete()
