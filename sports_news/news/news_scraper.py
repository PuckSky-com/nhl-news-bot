from django.utils.timezone import now
from news.utils.nhl_scraper import NHLScraper

class NewsScraperService:
    """
    A service class to handle news scraping from various sources.
    This can be used by both management commands and Celery tasks.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the news scraper service.
        
        Args:
            logger: A callable object with methods for logging (info, error, etc.)
                   If None, print statements will be used.
        """
        self.logger = logger
    
    def log_info(self, message):
        """Log an informational message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
    
    def log_error(self, message):
        """Log an error message."""
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def scrape_nhl_news(self):
        """
        Scrape news articles from NHL.com.
        
        Returns:
            Dict containing timestamp, count of articles scraped, and their titles.
        """
        try:
            self.log_info("Initializing NHL news scraper")
            scraper = NHLScraper()
            
            self.log_info("Starting scraping process")
            results = scraper.run()
            
            # Log results
            self.log_info(f"Scraping complete! Found {results['count']} new articles")
            
            if results['count'] > 0:
                self.log_info('New articles added:')
                for title in results['titles']:
                    self.log_info(f'- {title}')
            else:
                self.log_info('No new articles found')
            
            return {
                "timestamp": str(now()),
                "articles_scraped": results['count'],
                "titles": results.get('titles', [])
            }
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.log_error(f"Error running NHL scraper: {e}")
            self.log_error(error_traceback)
            
            return {
                "timestamp": str(now()),
                "articles_scraped": 0,
                "error": str(e),
                "traceback": error_traceback
            }