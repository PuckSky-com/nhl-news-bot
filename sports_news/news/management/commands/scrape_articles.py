
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.nhl_scraper import NHLScraper

class Command(BaseCommand):
    help = 'Scrapes NHL news articles and adds them to the database'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(f'Starting NHL news scraper at {timezone.now()}'))
            
            # Create and run the scraper
            scraper = NHLScraper()
            results = scraper.run()
            
            # Output results
            self.stdout.write(self.style.SUCCESS(f'Scraping complete! Found {results["count"]} new articles'))
            
            if results['count'] > 0:
                self.stdout.write(self.style.SUCCESS('New articles added:'))
                for title in results['titles']:
                    self.stdout.write(f'- {title}')
            else:
                self.stdout.write(self.style.SUCCESS('No new articles found'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running NHL scraper: {e}'))
            import traceback
            self.stderr.write(traceback.format_exc())