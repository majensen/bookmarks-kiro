# Product Overview

**Bookmark Enrichment Tool** - An application that processes CSV bookmark exports (like from Pocket) and enriches them with AI-generated content summaries and tags.

## Core Functionality
- Parse CSV bookmark files with title, URL, existing tags, and timestamps
- Visit each URL to scrape and analyze web content
- Generate concise descriptions (100-200 words) summarizing each site's content
- Create relevant tags (1-4 words each) based on content analysis
- Output enriched bookmark data with new descriptions and tags

## Key Considerations
- Handle various website structures and content types gracefully
- Implement rate limiting and respectful web scraping practices
- Provide robust error handling for unreachable/broken URLs
- Support resumable processing for large bookmark collections
- Consider content extraction challenges (JavaScript-heavy sites, paywalls, etc.)
- Maintain data integrity and provide clear progress feedback