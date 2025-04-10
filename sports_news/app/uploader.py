from app.utils.bluesky_post import upload_content, is_youtube_url
from app.utils import llm as llm
from django.db import transaction
from news.models import Article
from highlights.models import Video
import datetime

class ContentUploader:
    """
    A class to handle the uploading of articles and videos to Bluesky.
    This can be used by both management commands and Celery tasks.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the uploader.
        
        Args:
            logger: A callable object with methods for logging (info, error, etc.)
                   If None, print statements will be used.
        """
        self.logger = logger
    
    def log_info(self, message):
        """Log an informational message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
    
    def log_error(self, message):
        """Log an error message."""
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def upload_all(self):
        """Main method to upload all new articles and videos."""
        with transaction.atomic():
            # Fetch new articles and videos that are marked as 'is_new'
            new_articles = list(Article.objects.filter(is_new=True).select_for_update())
            new_videos = list(Video.objects.filter(is_new=True).select_for_update())

            # Mark items as processing (set `is_new` to False) to avoid duplicates
            for article in new_articles:
                article.is_new = False
                article.save()

            for video in new_videos:
                video.is_new = False
                video.save()

            # If no new articles or videos, we return early
            if not new_articles and not new_videos:
                self.log_info("No new articles or videos to upload.")
                return "No new articles or videos to upload."

            # Combine the lists of articles and videos, alternating between them
            combined_items = []
            max_items = max(len(new_articles), len(new_videos))

            for i in range(max_items):
                if i < len(new_articles):
                    combined_items.append(('article', new_articles[i]))
                if i < len(new_videos):
                    combined_items.append(('video', new_videos[i]))

            # Process items in alternating order
            for item_type, item in combined_items:
                if item_type == 'article':
                    self.upload_article(item)
                else:
                    self.upload_video(item)

            return f"Uploaded {len(new_articles)} articles and {len(new_videos)} videos."
    
    def upload_article(self, article: Article):
        """Uploads an article to Bluesky"""
        try:
            self.log_info(f"Starting upload for article: {article.title}")
            self.log_info(f"Contacting Ollama LLM service...")
            
            # Time the LLM call
            start_time = datetime.datetime.now()
            text = llm.send_request(article.title, article.description)
            end_time = datetime.datetime.now()
            
            self.log_info(f"LLM response received in {(end_time - start_time).total_seconds():.2f} seconds")
            self.log_info(f"Generated text: {text[:100]}...")
            
            # Continue with upload
            upload_content(
                text=text if text else article.title,
                title=article.title,
                link=article.link,
                description=article.description,
                img_url=article.img_url
            )
            self.log_info(f"Successfully uploaded article: {article.title} at {datetime.datetime.now()}")
        except Exception as e:
            import traceback
            self.log_error(f"Error uploading article '{article.title}': {str(e)}")
            self.log_error(traceback.format_exc())

    def upload_video(self, video: Video):
        """Uploads a video to Bluesky"""
        try:
            # Check if the video URL is a YouTube URL and extract the ID
            video_id = is_youtube_url(video.embed_url)

            # Use Llama to generate text for the video, passing description if available
            text = llm.send_request(video.title, video.description if hasattr(video, 'description') else "", highlight=True)

            upload_content(
                text=text if text else video.description,
                title=video.title,
                link=f"https://www.youtube.com/watch?v={video_id}",
                description="",
                img_url=video.img_url
            )
            self.log_info(f"Successfully uploaded video: {video.title} at {datetime.datetime.now()}")
        except Exception as e:
            self.log_error(f"Error uploading video '{video.title}': {e}")