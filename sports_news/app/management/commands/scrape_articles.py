from app.utils.scraper_utils import scrape_article, find_articles, save_article
from django.core.management.base import BaseCommand
from urllib.parse import urljoin
import datetime
import requests

class Command(BaseCommand):
    help = 'Scrape articles from NHL.com'

    def handle(self, *args, **kwargs):
        base_url = 'https://www.nhl.com'
        news_url = urljoin(base_url, 'news/')
        added = 0

        # Get the NHL news page.
        response = requests.get(news_url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to retrieve news page: {response.status_code}"))
            return

        articles = find_articles(response)

        for article in articles:
            relative_link = article.get('href')
            link = urljoin(base_url, relative_link)

            page_response = requests.get(link)
            if page_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to retrieve article from: {link}"))
                continue

            article_details = scrape_article(page_response)

            upload = save_article(
                        title = article_details['title'],
                        link= link,
                        desc= article_details['description'],
                        img_url= article_details['img_url']
                    )
            if upload:
                added += 1

                self.stdout.write(self.style.SUCCESS(
                    upload
                ))
        self.stdout.write(f'Added {added} article at {datetime.datetime.now()}')