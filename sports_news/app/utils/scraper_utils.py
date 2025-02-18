from bs4 import BeautifulSoup
from app.models import Article
from requests import Response
from app.utils.llama import send_request

def find_articles(response: Response):
    soup = BeautifulSoup(response.content, 'html.parser')

    sections = soup.find_all("section", class_="nhl-c-editorial-list")
    latest_news = sections[-1] if sections else None


    articles = latest_news.find_all("a", class_="nhl-c-card-wrap -story")

    return articles

def scrape_article(page_response: Response):
    article_page = BeautifulSoup(page_response.content, 'html.parser')

    title_tag = article_page.find("h1", class_="nhl-c-article__title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    description_tag = article_page.find("p", class_ = "nhl-c-article__summary")
    description = description_tag.get_text(strip=True) if description_tag else ""

    img_url = extract_thumbnail(article_page)
    if not img_url:
        img_url = "https://project-images-bucket.s3.us-east-1.amazonaws.com/nhl-logo.png"

    return {
        'title': title,
        'description': description,
        'img_url': img_url,
    }

def extract_body(article_page: BeautifulSoup):
    body_section = article_page.find("div", class_=["nhl-c-article__body", "d3-l-grid--inner"])
    if body_section:
        p_tags = body_section.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in p_tags)
        return content
    else:
        return "Body section not found"

def extract_thumbnail(article_page: BeautifulSoup):
    image_section = article_page.find("div", class_="nhl-c-article__header-image")

    img_tag = image_section.find("img")

    if img_tag and img_tag.has_attr("src"):
        return img_tag["src"]
    
    source_tag = image_section.find("source")
    if source_tag and source_tag.has_attr("srcset"):
        first_candidate = source_tag["srcset"].split(",")[0].strip()
        return first_candidate.split()[0]
    
    return None

def save_article(title: str, link: str, desc: str, img_url: str):
    if not Article.objects.filter(link=link).exists():
         
        content = send_request(title, desc)

        Article.objects.create(
              title = title,
              link = link,
              description = desc,
              content = content if content else title,
              img_url = img_url,
              is_new = True
        )
        return f"Added article -> {title}"