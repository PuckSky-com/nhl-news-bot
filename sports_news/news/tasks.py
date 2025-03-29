from celery import shared_task
from django.utils.timezone import now
from news.nhl_scraper import NHLScraper

@shared_task
def scrape_nhl_news():
    try:
        scraper = NHLScraper()
        results = scraper.run()
        return {"timestamp": str(now()), "articles_scraped": results['count']}
    except Exception as e:
        return {"error": str(e)}