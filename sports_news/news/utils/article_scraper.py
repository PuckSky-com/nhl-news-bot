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
        
    def run(self):
        """
        Execute the main scraping workflow.
        
        This method orchestrates the scraping process:
        1. Fetch the main page
        2. Extract target links
        3. Visit each link and scrape article content
        4. Save new articles to the database
        
        Returns:
            dict: Summary of scraping results with keys:
                - count (int): Number of new articles saved
                - titles (list): Titles of new articles saved
        """
        main_page = self._req_page(self.url)
        
        target_links = self.crawl_links(main_page)
        titles = []
        count = 0

        for link in target_links:
            article_page = self._req_page(link)

            article = self.scrape_page(article_page)
            img = self.extract_thumbnail(article_page)
            
            if article and img and not Article.objects.filter(link=link).exists():
                Article.objects.create(
                    title = article['title'],
                    description = article['description'],
                    link = link,
                    img_url = img,
                    is_new = True
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