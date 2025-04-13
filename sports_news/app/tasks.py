from celery import shared_task
from app.uploader import ContentUploader
from dotenv import load_dotenv
import logging
import os

load_dotenv()

pds_host = os.getenv('PDS_HOST')

logger = logging.getLogger(__name__)

@shared_task(bind=True, soft_time_limit=600, time_limit=18000)
def upload_to_bluesky(self):
    """Celery task to upload content to Bluesky"""
    task_logger = TaskLogger(self.request.id)
    uploader = ContentUploader(pds_url=pds_host, logger=task_logger)
    return uploader.upload_all()

class TaskLogger:
    """Logger adapter for Celery tasks that maintains consistent format"""
    def __init__(self, task_id):
        self.task_id = task_id
        
    def info(self, message):
        logger.info(f"Task {self.task_id}: {message}")
        
    def error(self, message):
        logger.error(f"Task {self.task_id}: {message}")