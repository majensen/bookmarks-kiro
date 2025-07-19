# Bookmark Enrichment Tool - Requirements Document

## Project Overview
A Python application that processes CSV bookmark exports (Pocket format) and enriches them with AI-generated content summaries, tags, author identification, and publisher detection.

## Functional Requirements

### Input Processing
- **Format**: CSV files with semicolon (`;`) delimiters
- **Expected Columns**: title, url, tags, created (timestamp)
- **Source**: Pocket bookmark exports or similar format
- **Volume**: Designed to handle 1000+ bookmarks

### Content Extraction
- **Web Scraping**: Visit each URL to extract content
- **Multi-Method Extraction**: 
  - Primary: newspaper3k library for article content
  - Fallback: BeautifulSoup for general web content
- **Rate Limiting**: Configurable delays between requests (default: 1 second)
- **Error Handling**: Graceful handling of unreachable/broken URLs

### AI-Powered Enhancement
- **Summarization**: Generate 100-200 word descriptions
- **Tagging**: Create 1-4 word tags (maximum 5 per bookmark)
- **People Detection**: Identify and tag people mentioned in content
- **Author Identification**: Extract page authors using multiple methods
- **Publisher Detection**: Identify publication/organization

### Content Analysis Rules
- **Neutral Tone**: Descriptions must be objective, factual, without promotional language
- **No Duplication**: Descriptions cannot repeat author, title, or publisher information
- **Content Focus**: Summaries focus on insights, arguments, and key points only
- **People Emphasis**: Special attention to identifying people central to content

### Output Specifications
- **Enhanced Title**: Format as "Original Title - Publisher"
- **Description**: 100-200 words, neutral tone, content-focused
- **AI Tags**: Mix of topical and people tags (1-4 words each)
- **Author**: Identified author name(s)
- **Preserved Data**: All original bookmark data maintained

## Technical Requirements

### Core Dependencies
```
requests>=2.31.0          # HTTP requests and web scraping
beautifulsoup4>=4.12.0    # HTML parsing and content extraction
pandas>=2.0.0             # CSV processing and data manipulation
openai>=1.0.0             # OpenAI API client
anthropic>=0.25.0         # Anthropic API client
newspaper3k>=0.2.8        # Article extraction and parsing
python-dotenv>=1.0.0      # Environment variable management
tqdm>=4.65.0              # Progress tracking and display
pyyaml>=6.0.0             # YAML configuration parsing
```

### Configuration Management
- **AI Provider Configuration**: YAML-based config supporting OpenAI, Anthropic, and local models
- **API Keys**: Provider-specific API keys via environment variables
- **Model Selection**: Configurable models per provider (GPT-4, Claude, Llama, etc.)
- **Processing Settings**: YAML-configured batch size, description length, tag limits
- **Output Format**: Configurable CSV delimiters and formats

### System Architecture
- **Modular Design**: Separate content extraction, AI processing, bookmark management
- **Error Recovery**: Comprehensive error handling with detailed logging
- **Resume Capability**: Ability to restart interrupted processing
- **Progress Tracking**: Real-time progress bars and status updates

### Performance Requirements
- **Batch Processing**: Process bookmarks in configurable batches (default: 10)
- **Memory Efficiency**: Handle large CSV files without memory issues
- **Network Resilience**: Robust handling of network timeouts and failures
- **Scalability**: Designed for processing thousands of bookmarks

## Output Schema

### Enhanced CSV Structure
| Column | Type | Description |
|--------|------|-------------|
| title | string | Original bookmark title |
| url | string | Original bookmark URL |
| tags | string | Original bookmark tags |
| created | integer | Original timestamp |
| description | string | AI-generated summary (100-200 words) |
| ai_tags | string | Comma-separated AI-generated tags |
| author | string | Identified page author(s) |
| formatted_title | string | Enhanced title with publisher |

### Processing Metadata
- **Progress Files**: Intermediate saves during processing
- **Summary Reports**: Success/failure statistics
- **Log Files**: Detailed processing logs for debugging

## User Interface Requirements

### Command Line Interface
```bash
python main.py input.csv [options]
  --output, -o     Output file path
  --resume, -r     Resume from previous run
  --verbose, -v    Verbose logging
```

### Configuration
- **Environment Setup**: `.env` file for API keys
- **Settings**: `config.py` for processing parameters
- **Cross-Platform**: Compatible with macOS, Linux, Windows

## Quality Requirements

### Content Quality
- **Accuracy**: Reliable extraction of titles, authors, publishers
- **Consistency**: Uniform formatting and structure across all records
- **Completeness**: Maximum information extraction from available content

### Technical Quality
- **Reliability**: Robust error handling and recovery
- **Performance**: Efficient processing of large bookmark collections
- **Maintainability**: Clean, modular code architecture
- **Logging**: Comprehensive logging for monitoring and debugging

## Constraints and Limitations

### Technical Constraints
- **AI Provider Dependency**: Requires API access for cloud providers (OpenAI/Anthropic) or local model setup
- **Network Dependency**: Requires internet access for content extraction and cloud AI APIs
- **Rate Limiting**: Must respect website rate limits, robots.txt, and AI provider rate limits

### Content Limitations
- **JavaScript Sites**: Limited support for heavily JavaScript-dependent sites
- **Paywalled Content**: Cannot access content behind paywalls
- **Dynamic Content**: May miss dynamically loaded content

### Processing Limitations
- **Language Support**: Optimized for English content
- **Content Types**: Best suited for articles and text-based content
- **Volume Limits**: Processing time scales with bookmark count and content complexity

## Success Criteria
- Successfully process 95%+ of accessible URLs
- Generate meaningful summaries for 90%+ of processed content
- Accurately identify authors for 80%+ of articles
- Complete processing of 1000+ bookmarks within reasonable time
- Provide resumable processing for interrupted sessions