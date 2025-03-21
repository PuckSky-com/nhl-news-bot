from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from django.utils import timezone
from highlights.yt_scraper import YouTubeScraper
import os

class Command(BaseCommand):
    help = 'Scrapes YouTube videos from a specified channel and adds them to the database'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(f'Starting YouTube scraper at {timezone.now()}'))

            load_dotenv()
            
            # Get API key from args or settings
            api_key = os.getenv('API_KEY')
            if not api_key:
                self.stdout.write(self.style.ERROR('No YouTube API key provided.'))
                return
            
            channel_id = "UCVhibwHk4WKw4leUt6JfRLg"
            
            # Create and run the scraper
            try:
                scraper = YouTubeScraper(
                    api_key=api_key,
                    channel_id=channel_id
                )
                
                results = scraper.get_latest_video(
                    max_results=5,
                    video_duration="medium"
                )
                
                # Output results
                self.stdout.write(self.style.SUCCESS(f'Scraping complete! Found {results["count"]} new videos'))
                
                if results['count'] > 0:
                    self.stdout.write(self.style.SUCCESS('New videos added:'))
                    for title in results['titles']:
                        self.stdout.write(f'- {title}')
                else:
                    self.stdout.write(self.style.SUCCESS('No new videos found'))
                    
                if 'error' in results:
                    self.stdout.write(self.style.WARNING(f'Warning: {results["error"]}'))
                    
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Configuration error: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running YouTube scraper: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())