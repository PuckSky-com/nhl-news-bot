# NHL News Scraper and Bluesky Uploader

## Overview
A sophisticated Django-based web scraping and content distribution system that automates the collection of NHL news articles and Sportsnet YouTube game recaps, generates AI-powered summaries, and publishes them to Bluesky.

## Key Features
- **Robust Web Scraping Architecture**
  - Abstract Scraper Design: Implements an extensible ScraperBase base class for news articles
  - Flexible Scraping Strategy: Supports multiple content sources with a consistent interface
  - Error Handling: Comprehensive error management and retry mechanisms
- **Content Sources**
  - NHL.com news articles
  - Sportsnet YouTube game recaps
- **Advanced Scraping Capabilities**
  - URL normalization to prevent duplicates
  - Intelligent link extraction
  - Thumbnail and metadata retrieval
  - Transactional database operations
- **AI-Powered Content Enhancement**
  - Uses Ollama with Mistral LLM for generating concise summaries
  - Supports context-aware summarization for articles and videos
- **Bluesky Publishing**
  - Automated content upload
  - Rich media embedding
  - Alternating publication of articles and videos
- **Scheduled Task Execution**
  - Celery-based task scheduling
  - Automated background processing
  - Configurable periodic tasks

## Technical Architecture

### Scraping Components
- **ScraperBase (Abstract Base Class)**
  - Provides a standardized scraping workflow
  - Key Methods:
    - `_req_page()`: Fetch and parse web pages
    - `_normalize_url()`: Prevent duplicate content
    - `run()`: Orchestrate entire scraping process
  - Abstract methods for subclasses to implement:
    - `scrape_page()`
    - `crawl_links()`
    - `extract_thumbnail()`
- **YouTubeScraper**
  - YouTube Data API integration
  - Features:
    - Sportsnet channel ID resolution
    - Resilient API request handling
    - Exponential backoff for rate limiting
    - Full video description retrieval

### Celery Tasks
- **Article Scraping Task**: Automated NHL news collection
- **Video Scraping Task**: Scheduled YouTube recap retrieval
- **Bluesky Upload Task**: Periodic content distribution
- **Task Monitoring**: Execution tracking and error handling

## Management Commands and Celery Tasks

### Manual Commands
- **Scrape NHL Articles**
  ```
  python manage.py scrape_articles
  ```
  - Fetches latest NHL news articles
  - Extracts comprehensive article metadata
  - Saves unique articles to database

- **Scrape Sportsnet YouTube Game Recaps**
  ```
  python manage.py scrape_videos
  ```
  - Retrieves latest NHL game recap videos
  - Extracts video metadata and descriptions
  - Saves new highlights

- **Upload to Bluesky**
  ```
  python manage.py upload
  ```
  - Retrieves new articles and videos
  - Generates AI summaries
  - Publishes alternating content to Bluesky

### Automated Celery Tasks
- **NHL News Scraping**
  ```python
  @shared_task
  def scrape_nhl_news():
      # Scheduled task for collecting NHL news
      # See news/tasks.py for implementation
  ```

- **YouTube Video Scraping**
  ```python
  @shared_task
  def scrape_youtube_videos():
      # Automated task for YouTube recap collection
      # See highlights/tasks.py for implementation
  ```

- **Bluesky Content Upload**
  ```python
  @shared_task
  def upload_to_bluesky():
      # Periodic task for content publishing
      # See app/tasks.py for implementation
  ```

## Configuration

### Environment Variables
Create a `.env` file:

```
PDS_HOST=<Bluesky PDS host>
USERNAME=<Bluesky username>
PASSWORD=<Bluesky password>
API_KEY=<YouTube Data API key>
SECRET_KEY=<Django secret key>
DB_PASSWORD=<PostgreSQL password>
DB_USER=<PostgreSQL user>
DB_NAME=<PostgreSQL name>
CELERY_URL=<Celery broker URL>
```

### Database Configuration
PostgreSQL database configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Celery Configuration
Configure Celery in `settings.py`:

```python
# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'scrape_nhl_news_every_hour': {
        'task': 'news.tasks.scrape_nhl_news',
        'schedule': crontab(minute=30, hour='*'),  # Runs every hour at 30 minutes past
    },
    'scrape_youtube_videos_every_hour': {
        'task': 'highlights.tasks.scrape_youtube_videos',
        'schedule': crontab(minute=30, hour='*'),  # Runs every hour at 30 minutes past
    },
    'upload_to_bluesky_every_hour': {
        'task': 'app.tasks.upload_to_bluesky',
        'schedule': crontab(minute=0, hour='*'),  # Runs every hour on the hour
    },
}
```

## Technologies
- Django
- PostgreSQL
- Celery & Celery Beat
- BeautifulSoup4
- Requests
- Ollama
- Mistral LLM
- YouTube Data API
- AT Protocol (Bluesky)
- Redis (Celery broker)

## Dependencies
- Django
- psycopg2-binary
- celery
- django-celery-beat
- redis
- beautifulsoup4
- requests
- langchain-ollama
- bluesky-atproto
- python-dotenv
- youtube-data-api

## Running the Application

### Manual Startup

#### Start Celery Worker
```
celery -A sports_news worker -l INFO
```

#### Start Celery Beat
```
celery -A sports_news beat -l INFO
```

#### Run Django Server
```
python manage.py runserver
```

### Automated Startup
Use the provided startup script:
```
./start_services.sh
```

The script provides the following features:
- Automatic activation of virtual environment
- Redis server startup and verification
- Celery worker and beat processes management
- Django server startup with error checking
- System resource monitoring (memory, disk, CPU)
- Comprehensive logging to a dedicated logs directory
- Process status reporting
- Graceful error handling and recovery

To stop all services:
```
pkill -f 'celery|redis-server|python.*manage.py'
```

## Roadmap
- Expand scraping sources
- Implement advanced content filtering
- Enhance AI summarization techniques
- Add comprehensive logging
- Create monitoring dashboard
- Improve Celery task scheduling
- Implement task result monitoring

## Performance Considerations
- Transactional database operations
- URL normalization
- Exponential backoff for API requests
- Configurable scraping parameters
- Task concurrency management
- Task priority scheduling
- PostgreSQL database optimization

## License
MIT License - See the LICENSE file for details.

## Contributing
Contributions are welcome! Please submit pull requests or open issues to suggest improvements.