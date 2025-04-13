from django.core.management.base import BaseCommand
from django.utils import timezone
from highlights.video_scraper import VideoScraperService

class Command(BaseCommand):
    help = 'Scrapes YouTube videos from a specified channel and adds them to the database'

    def add_arguments(self, parser):
        parser.add_argument('--channel-id', type=str, help='YouTube channel ID to scrape')
        parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results to fetch')
        parser.add_argument('--duration', type=str, default='medium', 
                          choices=['short', 'medium', 'long'], 
                          help='Duration filter for videos')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Starting YouTube scraper at {timezone.now()}'))
        
        command_logger = CommandLogger(self)
        scraper_service = VideoScraperService(logger=command_logger)
        
        results = scraper_service.scrape_videos(
            channel_id=options.get('channel_id'),
            max_results=options.get('max_results'),
            video_duration=options.get('duration')
        )
        
        self.stdout.write(self.style.SUCCESS(f'Scraping complete! Found {results["videos_scraped"]} new videos'))

class CommandLogger:
    """Logger adapter for Django commands that uses Django's stdout/stderr"""
    def __init__(self, command):
        self.command = command
        
    def info(self, message):
        self.command.stdout.write(self.command.style.SUCCESS(message))
        
    def error(self, message):
        self.command.stdout.write(self.command.style.ERROR(message))
        
    def warning(self, message):
        self.command.stdout.write(self.command.style.WARNING(message))