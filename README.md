# NHL News Scraper and Bluesky Uploader

## Overview

A sophisticated Django-based web scraping and content distribution system that automates the collection of NHL news articles and Sportsnet YouTube game recaps, generates AI-powered summaries, and publishes them to Bluesky.

## Key Features

### Robust Web Scraping Architecture
- **Abstract Scraper Design**: Implements an extensible `ArticleScraper` base class
- **Flexible Scraping Strategy**: Supports multiple content sources with a consistent interface
- **Error Handling**: Comprehensive error management and retry mechanisms

### Content Sources
- NHL.com news articles
- Sportsnet YouTube game recaps

### Advanced Scraping Capabilities
- URL normalization to prevent duplicates
- Intelligent link extraction
- Thumbnail and metadata retrieval
- Transactional database operations

### AI-Powered Content Enhancement
- Uses Ollama with Mistral LLM for generating concise summaries
- Supports context-aware summarization for articles and videos

### Bluesky Publishing
- Automated content upload
- Rich media embedding
- Alternating publication of articles and videos

## Technical Architecture

### Scraping Components

#### ArticleScraper (Abstract Base Class)
- Provides a standardized scraping workflow
- Key Methods:
  - `_req_page()`: Fetch and parse web pages
  - `_normalize_url()`: Prevent duplicate content
  - `run()`: Orchestrate entire scraping process
- Abstract methods for subclasses to implement:
  - `scrape_page()`
  - `crawl_links()`
  - `extract_thumbnail()`

#### YouTubeScraper
- YouTube Data API integration
- Features:
  - Sportsnet channel ID resolution
  - Resilient API request handling
  - Exponential backoff for rate limiting
  - Full video description retrieval

### Project Structure

```
sports_news/
├── app/
│   ├── management/commands/
│   │   └── upload.py
│   └── utils/
│       ├── bluesky_post.py
│       ├── llama.py
│       └── prompts.py
├── highlights/
│   ├── management/commands/
│   │   └── scrape_videos.py
│   └── yt_scraper.py
├── news/
│   ├── management/commands/
│   │   └── scrape_articles.py
│   ├── utils/
│   │   └── article_scraper.py
│   └── nhl_scraper.py
└── sports_news/
    ├── settings.py
    └── urls.py
```

## Management Commands

### Scrape NHL Articles
```bash
python manage.py scrape_articles
```
- Fetches latest NHL news articles
- Extracts comprehensive article metadata
- Saves unique articles to database

### Scrape Sportsnet YouTube Game Recaps
```bash
python manage.py scrape_videos
```
- Retrieves latest NHL game recap videos
- Extracts video metadata and descriptions
- Saves new highlights

### Upload to Bluesky
```bash
python manage.py upload
```
- Retrieves new articles and videos
- Generates AI summaries
- Publishes alternating content to Bluesky

## Configuration

### Environment Variables
Create a `.env` file:

```
PDS_HOST=<Bluesky PDS host>
USERNAME=<Bluesky username>
PASSWORD=<Bluesky password>
API_KEY=<YouTube Data API key>
```

## Technologies

- Django
- BeautifulSoup4
- Requests
- Ollama
- Mistral LLM
- YouTube Data API
- AT Protocol (Bluesky)

## Dependencies

- Django
- beautifulsoup4
- requests
- langchain-ollama
- bluesky-atproto
- python-dotenv
- youtube-data-api

## Roadmap

- [ ] Expand scraping sources
- [ ] Implement advanced content filtering
- [ ] Enhance AI summarization techniques
- [ ] Add comprehensive logging
- [ ] Create monitoring dashboard

## Performance Considerations

- Transactional database operations
- URL normalization
- Exponential backoff for API requests
- Configurable scraping parameters

## License

MIT License - See the LICENSE file for details.

## Contributing

Contributions are welcome! Please submit pull requests or open issues to suggest improvements.

