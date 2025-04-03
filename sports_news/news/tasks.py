# sports_news/news/tasks.py
from celery import shared_task
from news.utils.news_scraper import NewsScraperService
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_nhl_news():
    """Celery task to scrape NHL news and add them to the database"""
    task_logger = TaskLogger()
    scraper_service = NewsScraperService(logger=task_logger)
    return scraper_service.scrape_nhl_news()

class TaskLogger:
    """Logger adapter for Celery tasks that logs to the Celery logger"""
    def info(self, message):
        logger.info(message)
        
    def error(self, message):
        logger.error(message)