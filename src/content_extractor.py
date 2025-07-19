import requests
import time
from bs4 import BeautifulSoup
from newspaper import Article
import logging
from typing import Optional, Dict, Any

from config import USER_AGENT, REQUEST_DELAY, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extracts and processes web content from URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a URL.
        
        Returns:
            Dict with 'title', 'text', 'authors', 'publish_date' or None if failed
        """
        try:
            # Add delay to be respectful
            time.sleep(REQUEST_DELAY)
            
            # Try newspaper3k first (better for articles)
            try:
                article = Article(url)
                article.download()
                article.parse()
                
                if article.text and len(article.text.strip()) > 100:
                    # Try to get publisher from newspaper3k or URL
                    publisher = self._extract_publisher_from_url(url)
                    
                    return {
                        'title': article.title or '',
                        'text': article.text,
                        'authors': article.authors,
                        'publisher': publisher,
                        'publish_date': article.publish_date,
                        'method': 'newspaper'
                    }
            except Exception as e:
                logger.debug(f"Newspaper extraction failed for {url}: {e}")
            
            # Fallback to BeautifulSoup
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else ''
            
            # Extract author and publisher
            author = self._extract_author(soup)
            publisher = self._extract_publisher(soup, url)
            
            # Extract main content
            text = self._extract_main_text(soup)
            
            if text and len(text.strip()) > 50:
                return {
                    'title': title,
                    'text': text,
                    'authors': [author] if author else [],
                    'publisher': publisher,
                    'publish_date': None,
                    'method': 'beautifulsoup'
                }
            
            logger.warning(f"Insufficient content extracted from {url}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return None
    
    def _extract_publisher(self, soup: BeautifulSoup, url: str) -> str:
        """Extract publisher information from HTML soup and URL."""
        
        # Common publisher selectors
        publisher_selectors = [
            'meta[property="og:site_name"]',
            'meta[name="application-name"]',
            'meta[name="publisher"]',
            '.site-name',
            '.publisher',
            '.source',
            '[itemprop="publisher"]'
        ]
        
        for selector in publisher_selectors:
            publisher_elem = soup.select_one(selector)
            if publisher_elem:
                if publisher_elem.name == 'meta':
                    publisher = publisher_elem.get('content', '').strip()
                else:
                    publisher = publisher_elem.get_text(strip=True)
                
                if publisher and len(publisher) < 100:  # Reasonable publisher name length
                    return publisher
        
        # Fallback: extract from URL domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. and common subdomains
            domain = domain.replace('www.', '').replace('m.', '')
            # Convert domain to title case
            if '.' in domain:
                publisher = domain.split('.')[0].title()
                return publisher
        except:
            pass
        
        return ''
    
    def _extract_publisher_from_url(self, url: str) -> str:
        """Extract publisher from URL domain as fallback."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. and common subdomains
            domain = domain.replace('www.', '').replace('m.', '')
            # Convert domain to title case
            if '.' in domain:
                publisher = domain.split('.')[0].title()
                return publisher
        except:
            pass
        return ''
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author information from HTML soup."""
        
        # Common author selectors
        author_selectors = [
            '[rel="author"]',
            '.author',
            '.byline',
            '.author-name',
            '.post-author',
            '.article-author',
            '[class*="author"]',
            '[itemprop="author"]',
            'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == 'meta':
                    author = author_elem.get('content', '').strip()
                else:
                    author = author_elem.get_text(strip=True)
                
                if author and len(author) < 100:  # Reasonable author name length
                    # Clean up common prefixes
                    author = author.replace('By ', '').replace('by ', '').strip()
                    return author
        
        return ''
    
    def _extract_main_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML soup."""
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try common content selectors
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-body',
            'main'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Reasonable content length
                    return text
        
        # Fallback to body text
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)