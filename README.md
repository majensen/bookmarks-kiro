# Bookmark Enrichment Tool

A Python application that processes CSV bookmark exports and enriches them with AI-generated content summaries and tags.

## Features

- Parse CSV bookmark files (Pocket export format)
- Visit URLs to scrape and analyze web content
- Generate concise descriptions (100-200 words) for each bookmark
- Create relevant tags (1-4 words each) based on content analysis
- **Author identification** - extracts and identifies page authors using multiple methods
- **Special focus on people detection** - identifies and tags people mentioned in content
- Export enriched data with new descriptions and AI-generated tags
- Resume capability for interrupted processing
- Progress tracking and error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your AI provider API key
```

3. Configure AI provider in `config.yaml`:
```yaml
ai:
  provider: "openai"  # Options: openai, anthropic, local
  model: "gpt-3.5-turbo"
```

3. Run the enrichment process:
```bash
python main.py pocket-bookmarks.csv
```

## Configuration

- **AI Provider**: Configure in `config.yaml` - supports OpenAI, Anthropic, or local models
- **API Keys**: Set in `.env` file based on your chosen provider
- **Processing Settings**: Adjust scraping delays, batch sizes, and output formats in `config.yaml`

## Output

The tool generates an enriched CSV with additional columns:
- `description` - AI-generated summary (100-200 words)
- `ai_tags` - Content-based tags (1-4 words each), including people mentioned
- `author` - Identified author(s) of the page content

## Author Detection

The system uses multiple approaches to identify content authors:
- HTML metadata extraction (author meta tags, bylines, etc.)
- Content analysis via newspaper3k library
- AI-powered author identification from content
- Combines detected authors with AI analysis for accuracy

## People Detection

The AI processor specifically looks for and extracts people mentioned in the content:
- Names of authors, subjects, or key figures discussed
- People tags are included alongside topical tags
- Helps organize bookmarks by the people they reference