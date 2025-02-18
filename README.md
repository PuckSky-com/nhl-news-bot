# NHL News Scraper and Bluesky Uploader

## Overview
This project automates the process of scraping NHL.com for news articles, saving them to a database, generating short summaries using an AI model, and posting them to Bluesky with embedded links and images.

## Features
- **Scrapes NHL News Articles**: Extracts article details such as title, description, and images from NHL.com
- **Stores Articles in a Database**: Saves the scraped articles to prevent duplicate entries
- **AI-Generated Summaries**: Uses a language model to create concise and engaging social media summaries
- **Bluesky Integration**: Automatically posts new articles to Bluesky with an external embed, including a link and thumbnail

## Project Structure

### Management Commands

1. **Scraping Command** (`scrape_articles`)
   - Fetches NHL news page
   - Extracts article links and metadata
   - Saves new articles to the database

2. **Bluesky Posting Command** (`upload_articles`)
   - Retrieves newly scraped articles
   - Posts them to Bluesky with an external embed
   - Marks articles as uploaded or deletes them in case of failure

### Utility Modules

#### `scraper_utils.py`
- Functions for parsing NHL.com's HTML structure using BeautifulSoup
- Extracts titles, descriptions, article bodies, and images
- Saves articles with AI-generated summaries

#### `bluesky_post.py`
- Handles posting articles to Bluesky
- Uses the AT Protocol client for authentication and content uploads
- Supports external embeds with links and thumbnails

#### `llama.py`
- Calls an AI model to generate short-form article summaries
- Ensures clear and concise output for social media

## Environment Variables
Set up a `.env` file with the following:
```
PDS_HOST=<Bluesky PDS host>
USERNAME=<Bluesky account username>
PASSWORD=<Bluesky account password>
API_TOKEN=<API key for AI-generated summaries>
```

## Running the Scraper and Uploader

1. **Scrape NHL articles:**
```bash
python manage.py scrape_articles
```

2. **Upload new articles to Bluesky:**
```bash
python manage.py upload_articles
```

## Dependencies
- Django
- BeautifulSoup4
- Requests
- AT Protocol Python Client
- OpenAI Python SDK
- Python Dotenv

## Future Improvements
- Enhance error handling and logging
- Expand to multiple news sources
- Support for additional social media platforms

## License
This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```