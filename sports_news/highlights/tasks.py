# highlights/tasks.py
from celery import shared_task
from highlights.video_scraper import VideoScraperService
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_youtube_videos(channel_id=None, max_results=10, video_duration="medium"):
    """Celery task to scrape YouTube videos and add them to the database"""
    task_logger = TaskLogger()
    scraper_service = VideoScraperService(logger=task_logger)
    return scraper_service.scrape_videos(
        channel_id=channel_id,
        max_results=max_results,
        video_duration=video_duration
    )

class TaskLogger:
    """Logger adapter for Celery tasks that logs to the Celery logger"""
    def info(self, message):
        logger.info(message)
        
    def error(self, message):
        logger.error(message)
        
    def warning(self, message):
        logger.warning(message)