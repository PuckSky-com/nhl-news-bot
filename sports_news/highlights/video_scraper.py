from highlights.utils.yt_scraper import YouTubeScraper
import os
from dotenv import load_dotenv

class VideoScraperService:
    """
    A service class to handle YouTube video scraping.
    This can be used by both management commands and Celery tasks.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the video scraper service.
        
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
    
    def log_warning(self, message):
        """Log a warning message."""
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
            
    def scrape_videos(self, channel_id=None, max_results=10, video_duration="medium"):
        """
        Main method to scrape latest videos from YouTube.
        
        Args:
            channel_id: The YouTube channel ID to scrape. Default is NHL channel.
            max_results: Maximum number of results to retrieve.
            video_duration: Duration filter for videos ('short', 'medium', 'long').
            
        Returns:
            Dict containing count of videos scraped and their titles.
        """
        try:
            # Load environment variables if not already loaded
            load_dotenv()
            
            # Get API key from environment
            api_key = os.getenv('API_KEY')
            if not api_key:
                self.log_error('No YouTube API key provided.')
                return {"videos_scraped": 0, "titles": [], "error": "No API key provided"}
            
            # Use default channel if none provided
            if not channel_id:
                channel_id = "UCVhibwHk4WKw4leUt6JfRLg"  # NHL channel ID
            
            # Create and run the scraper
            try:
                self.log_info(f"Initializing YouTube scraper for channel ID: {channel_id}")
                scraper = YouTubeScraper(
                    api_key=api_key,
                    channel_id=channel_id
                )
                
                self.log_info(f"Fetching latest videos (max: {max_results}, duration: {video_duration})")
                results = scraper.get_latest_video(
                    max_results=max_results,
                    video_duration=video_duration
                )
                
                # Log results
                self.log_info(f"Scraping complete! Found {results['count']} new videos")
                
                if results['count'] > 0:
                    self.log_info('New videos added:')
                    for title in results['titles']:
                        self.log_info(f'- {title}')
                else:
                    self.log_info('No new videos found')
                    
                if 'error' in results:
                    self.log_warning(f'Warning during scraping: {results["error"]}')
                
                return {
                    "videos_scraped": results["count"],
                    "titles": results["titles"],
                    "error": results.get("error")
                }
                    
            except ValueError as e:
                self.log_error(f'Configuration error: {e}')
                return {"videos_scraped": 0, "titles": [], "error": str(e)}
                
        except Exception as e:
            import traceback
            self.log_error(f'Error running YouTube scraper: {e}')
            self.log_error(traceback.format_exc())
            return {"videos_scraped": 0, "titles": [], "error": str(e)}