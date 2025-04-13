# app/management/commands/upload.py
from django.core.management.base import BaseCommand
from app.uploader import ContentUploader
from dotenv import load_dotenv
import os

load_dotenv()

pds_host = os.getenv('PDS_HOST')

class Command(BaseCommand):
    help = "Uploads new articles and videos from the database to Bluesky with external embed support"

    def handle(self, *args, **kwargs):
        # Create a logger adapter that uses Django's stdout/stderr
        command_logger = CommandLogger(self)
        uploader = ContentUploader(pds_url=pds_host, logger=command_logger)
        uploader.upload_all()

class CommandLogger:
    """Logger adapter for Django commands that uses Django's stdout/stderr"""
    def __init__(self, command):
        self.command = command
        
    def info(self, message):
        self.command.stdout.write(self.command.style.SUCCESS(message))
        
    def error(self, message):
        self.command.stdout.write(self.command.style.ERROR(message))