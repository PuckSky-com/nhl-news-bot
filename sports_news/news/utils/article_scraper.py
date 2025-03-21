from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from news.models import Article

class ArticleScraper(ABC):
    """
    Abstract base class for web scrapers.
    Defines the common interface that all scrapers should implement.
    
    This class provides a foundation for building website scrapers with a consistent
    interface. It handles the main scraping workflow while allowing subclasses to
    implement site-specific scraping logic.
    
    Attributes:
        url (str): The base URL to scrape content from
    """

    def __init__(self, url):
        """
        Initialize the scraper with a target URL.
        
        Args:
            url (str): The base URL to scrape content from
        """
        self.url = url

    @staticmethod
    def _req_page(url: str) -> BeautifulSoup:
        """
        Request a webpage and parse it with BeautifulSoup.
        
        Args:
            url (str): The URL to request
            
        Returns:
            BeautifulSoup: Parsed HTML content or None if request failed
        """
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve page: {response.status_code}")
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return None
        
    @staticmethod
    def _normalize_url(url):
        """Normalize URL to prevent duplicates from minor URL variations"""
        # Remove trailing slashes
        url = url.rstrip('/')
        # Remove common tracking parameters
        import re
        url = re.sub(r'\?(utm_.*|fb_.*|source=.*|ref=.*)', '', url)
        return url
        
    def run(self):
        """Improved run method with transaction and better error handling"""
        from django.db import transaction
        
        main_page = self._req_page(self.url)
        if not main_page:
            return {'count': 0, 'titles': []}
            
        target_links = self.crawl_links(main_page)
        titles = []
        count = 0

        for link in target_links:
            # Normalize the link to prevent duplicates from URL variations
            normalized_link = self._normalize_url(link)
            
            # Use transactions to prevent race conditions
            with transaction.atomic():
                # Check again inside transaction to prevent race conditions
                if Article.objects.filter(link=normalized_link).exists():
                    continue
                    
                article_page = self._req_page(link)
                if not article_page:
                    continue

                article = self.scrape_page(article_page)
                img = self.extract_thumbnail(article_page)
                
                if article and img:
                    Article.objects.create(
                        title=article['title'],
                        description=article['description'],
                        link=normalized_link,
                        img_url=img,
                        is_new=True
                    )
                    titles.append(f"Uploaded: {article['title']}")
                    count += 1
                    
        return {
            'count': count,
            'titles': titles
        }

    @abstractmethod  
    def scrape_page(self, page: BeautifulSoup) -> dict:
        """
        Extract article data from a page.
        
        Args:
            page (BeautifulSoup): Parsed HTML content of an article page
            
        Returns:
            Article: Extracted article data
        """
        pass

    @abstractmethod
    def crawl_links(self, page: BeautifulSoup) -> list:
        """
        Extract article links from the main page.
        
        Args:
            page (BeautifulSoup): Parsed HTML content of the main page
            
        Returns:
            list: List of URLs to scrape for articles
        """
        pass

    @abstractmethod
    def extract_thumbnail(self, page: BeautifulSoup) -> str:
        """
        Extract thumbnail image URL from a page.
        
        Args:
            page (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: URL of the thumbnail image
        """
        pass