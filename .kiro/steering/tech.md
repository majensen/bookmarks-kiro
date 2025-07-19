# Technology Stack

## Recommended Stack

- **Language**: Python (excellent for web scraping, CSV processing, and AI integration)
- **Web Scraping**: requests + BeautifulSoup or Scrapy
- **Content Processing**: newspaper3k or similar for article extraction
- **AI/Summarization**: OpenAI API, Anthropic Claude, or local models
- **CSV Processing**: pandas for data manipulation
- **Rate Limiting**: time.sleep() or more sophisticated throttling

## Development Standards

- Use consistent code formatting with black/autopep8
- Implement comprehensive error handling for network requests
- Add logging for processing progress and debugging
- Use configuration files for API keys and settings
- Follow semantic versioning for releases
- Use meaningful commit messages following conventional commit format

## Key Requirements

- Respectful web scraping (user agents, delays, robots.txt compliance)
- Robust error handling for failed URL requests
- Progress tracking for long-running operations
- Configurable output formats (CSV, JSON, etc.)
- Resume capability for interrupted processing

## Dependencies

- Core: requests, beautifulsoup4, pandas, openai/anthropic
- Development: pytest, black, flake8
- Optional: newspaper3k, scrapy, selenium (for JS-heavy sites)
