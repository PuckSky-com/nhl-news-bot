from celery import shared_task
from app.utils.bluesky_post import upload_content, is_youtube_url
from app.utils import llama as llm
from django.db import transaction
from news.models import Article
from highlights.models import Video
import datetime

@shared_task(bind=True, soft_time_limit=600, time_limit=1800)
def upload_to_bluesky(self):
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
                upload_article(item)
            else:
                upload_video(item)

        return f"Uploaded {len(new_articles)} articles and {len(new_videos)} videos."

def upload_article(article: Article):
    """Uploads an article to Bluesky"""
    try:
        print(f"Starting upload for article: {article.title}")
        print(f"Contacting Ollama LLM service...")
        
        # Time the LLM call
        start_time = datetime.time()
        text = llm.send_request_direct(article.title, article.description)
        end_time = datetime.time()
        
        print(f"LLM response received in {end_time - start_time:.2f} seconds")
        print(f"Generated text: {text[:100]}...")
        
        # Continue with upload
        upload_content(
            text=text if text else article.title,
            title=article.title,
            link=article.link,
            description=article.description,
            img_url=article.img_url
        )
        print(f"Successfully uploaded article: {article.title} at {datetime.datetime.now()}")
    except Exception as e:
        import traceback
        print(f"Error uploading article '{article.title}': {str(e)}")
        print(traceback.format_exc())

def upload_video(video: Video):
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
        print(f"Successfully uploaded video: {video.title} at {datetime.datetime.now()}")
    except Exception as e:
        print(f"Error uploading video '{video.title}': {e}")
