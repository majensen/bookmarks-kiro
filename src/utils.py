import logging
import sys
from pathlib import Path

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'bookmark_processor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('newspaper').setLevel(logging.WARNING)

def validate_url(url: str) -> bool:
    """Basic URL validation."""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    return url.startswith(('http://', 'https://'))

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common artifacts
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    return text.strip()

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length, preserving word boundaries."""
    if len(text) <= max_length:
        return text
    
    # Find last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If space is reasonably close to end
        return truncated[:last_space] + '...'
    else:
        return truncated + '...'