import os
from celery import shared_task
from highlights.yt_scraper import YouTubeScraper
from dotenv import load_dotenv

@shared_task
def scrape_youtube_videos():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    channel_id = "UCVhibwHk4WKw4leUt6JfRLg"

    scraper = YouTubeScraper(api_key=api_key, channel_id=channel_id)
    results = scraper.get_latest_video(max_results=10, video_duration="medium")

    return {"videos_scraped": results["count"], "titles": results["titles"]}
