# sports_news/news/management/commands/scrape_nhl.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from sports_news.news.utils.news_scraper import NewsScraperService

class Command(BaseCommand):
    help = 'Scrapes NHL news articles and adds them to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Starting NHL news scraper at {timezone.now()}'))
        
        command_logger = CommandLogger(self)
        scraper_service = NewsScraperService(logger=command_logger)
        
        results = scraper_service.scrape_nhl_news()
        
        if 'error' in results:
            self.stdout.write(self.style.ERROR(f"Scraping failed with error: {results['error']}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Scraping complete at {results['timestamp']}. "
                                 f"Found {results['articles_scraped']} new articles.")
            )

class CommandLogger:
    """Logger adapter for Django commands that uses Django's stdout/stderr"""
    def __init__(self, command):
        self.command = command
        
    def info(self, message):
        self.command.stdout.write(self.command.style.SUCCESS(message))
        
    def error(self, message):
        self.command.stdout.write(self.command.style.ERROR(message))