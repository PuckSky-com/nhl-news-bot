from news.utils.article_scraper import ArticleScraper

class NHLScraper(ArticleScraper):

    def __init__(self):
        super().__init__("https://www.nhl.com/news/")

    def crawl_links(self, page):
        sections = page.find_all("section", class_="nhl-c-editorial-list")
        latest_news = sections[-1] if sections else None
        
        article_elements = latest_news.find_all("a", class_="nhl-c-card-wrap -story")
        # Extract URLs from the article elements
        article_links = [element.get('href') for element in article_elements if element.has_attr('href')]
        
        # Check if URLs are relative and add domain if needed
        full_links = []
        for link in article_links:
            if link.startswith('/'):
                full_links.append(f"https://www.nhl.com{link}")
            else:
                full_links.append(link)
        
        return full_links
        
    def scrape_page(self, page):
        title_tag = page.find("h1", class_="nhl-c-article__title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        description_tag = page.find("p", class_ = "nhl-c-article__summary")
        description = description_tag.get_text(strip=True) if description_tag else ""

        return {
            'title': title,
            'description': description,
        }
    
    def extract_thumbnail(self, page):
        image_section = page.find("div", class_="nhl-c-article__header-image")
    
        if image_section:
            # Try to find direct img tag
            img_tag = image_section.find("img")
            if img_tag and img_tag.has_attr("src"):
                return img_tag["src"]
            
            # Try to find source tag with srcset
            source_tag = image_section.find("source")
            if source_tag and source_tag.has_attr("srcset"):
                first_candidate = source_tag["srcset"].split(",")[0].strip()
                return first_candidate.split()[0]
        
        # If no standard image found, look for video poster image
        video_poster = page.find("div", class_="vjs-poster")
        if video_poster:
            img_tag = video_poster.find("img")
            if img_tag and img_tag.has_attr("src"):
                return img_tag["src"]
        
        # If no image found, return None
        return None