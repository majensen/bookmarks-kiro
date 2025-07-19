import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from tqdm import tqdm
import time

from .content_extractor import ContentExtractor
from .ai_processor import AIProcessor
from config import BATCH_SIZE

logger = logging.getLogger(__name__)

class BookmarkProcessor:
    """Main processor for enriching bookmark CSV files."""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
        self.ai_processor = AIProcessor()
    
    def process_file(self, input_path: Path, output_path: Path, output_format: str = 'csv', resume: bool = False):
        """Process a bookmark CSV file and enrich it with summaries and tags."""
        
        logger.info(f"Starting bookmark processing: {input_path}")
        
        # Load CSV
        df = self._load_csv(input_path)
        if df is None:
            return
        
        # Handle resume functionality
        if resume and output_path.exists():
            df = self._handle_resume(df, output_path)
        else:
            # Add new columns for enriched data
            df['description'] = ''
            df['ai_tags'] = ''
            df['author'] = ''
            df['formatted_title'] = ''
            df['processing_status'] = 'pending'
        
        # Process bookmarks
        total_pending = len(df[df['processing_status'] == 'pending'])
        logger.info(f"Processing {total_pending} bookmarks")
        
        with tqdm(total=total_pending, desc="Processing bookmarks") as pbar:
            for idx, row in df.iterrows():
                if row['processing_status'] != 'pending':
                    continue
                
                try:
                    result = self._process_bookmark(row)
                    
                    # Update dataframe
                    df.at[idx, 'description'] = result['description']
                    df.at[idx, 'ai_tags'] = ', '.join(result['tags'])
                    df.at[idx, 'author'] = result['author']
                    df.at[idx, 'formatted_title'] = result.get('formatted_title', row.get('title', ''))
                    df.at[idx, 'processing_status'] = 'completed'
                    
                    pbar.update(1)
                    
                    # Save progress periodically
                    if (idx + 1) % BATCH_SIZE == 0:
                        self._save_progress(df, output_path, output_format)
                        logger.info(f"Saved progress: {idx + 1} bookmarks processed")
                
                except Exception as e:
                    logger.error(f"Failed to process bookmark {idx}: {e}")
                    df.at[idx, 'processing_status'] = 'failed'
                    df.at[idx, 'description'] = 'Processing failed'
                    df.at[idx, 'author'] = ''
                    df.at[idx, 'formatted_title'] = row.get('title', '')
                    pbar.update(1)
        
        # Final save
        self._save_final_output(df, output_path, output_format)
        logger.info(f"Processing complete. Output saved to: {output_path}")
    
    def _load_csv(self, input_path: Path) -> Optional[pd.DataFrame]:
        """Load and validate the input CSV file."""
        try:
            # Try different separators
            for sep in [';', ',', '\t']:
                try:
                    df = pd.read_csv(input_path, sep=sep)
                    if len(df.columns) >= 3:  # Should have at least title, url, tags
                        logger.info(f"Loaded CSV with separator '{sep}': {len(df)} rows, {len(df.columns)} columns")
                        return df
                except:
                    continue
            
            logger.error(f"Could not parse CSV file: {input_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return None
    
    def _handle_resume(self, df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
        """Handle resuming from a previous run."""
        try:
            # Try to detect format from file extension
            if output_path.suffix.lower() == '.tsv':
                existing_df = pd.read_csv(output_path, sep='\t')
            else:
                existing_df = pd.read_csv(output_path, sep=',')
            
            # Merge with existing progress
            if 'processing_status' in existing_df.columns:
                # Update status for existing entries
                for idx, row in existing_df.iterrows():
                    if idx < len(df):
                        df.at[idx, 'description'] = row.get('description', '')
                        df.at[idx, 'ai_tags'] = row.get('ai_tags', '')
                        df.at[idx, 'author'] = row.get('author', '')
                        df.at[idx, 'formatted_title'] = row.get('formatted_title', '')
                        df.at[idx, 'processing_status'] = row.get('processing_status', 'pending')
            
            logger.info("Resuming from previous run")
            return df
            
        except Exception as e:
            logger.warning(f"Could not resume from existing file: {e}")
            # Add new columns for fresh start
            df['description'] = ''
            df['ai_tags'] = ''
            df['author'] = ''
            df['formatted_title'] = ''
            df['processing_status'] = 'pending'
            return df
    
    def _process_bookmark(self, row: pd.Series) -> dict:
        """Process a single bookmark."""
        url = row['url']
        title = row.get('title', '')
        existing_tags = row.get('tags', '')
        
        logger.debug(f"Processing: {url}")
        
        # Extract content
        content_data = self.content_extractor.extract_content(url)
        
        if not content_data:
            return {
                'description': f"Could not access content from: {title or url}",
                'tags': [],
                'author': '',
                'formatted_title': title or url
            }
        
        # Use extracted title if original is missing or just URL
        if not title or title == url:
            title = content_data['title']
        
        # Process with AI
        result = self.ai_processor.process_content(
            title=title,
            content=content_data['text'],
            authors=content_data.get('authors', []),
            publisher=content_data.get('publisher', ''),
            existing_tags=existing_tags
        )
        
        # Format title with publisher if available
        publisher = content_data.get('publisher', '')
        if publisher and title:
            formatted_title = f"{title} - {publisher}"
            result['formatted_title'] = formatted_title
        else:
            result['formatted_title'] = title
        
        return result
    
    def _save_progress(self, df: pd.DataFrame, output_path: Path, output_format: str = 'csv'):
        """Save current progress to file."""
        try:
            self._write_dataframe(df, output_path, output_format)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def _save_final_output(self, df: pd.DataFrame, output_path: Path, output_format: str = 'csv'):
        """Save final enriched output."""
        try:
            # Remove processing status column for final output
            output_df = df.drop('processing_status', axis=1, errors='ignore')
            self._write_dataframe(output_df, output_path, output_format)
            
            # Also save a summary
            summary_path = output_path.parent / f"{output_path.stem}_summary.txt"
            self._save_summary(df, summary_path)
            
        except Exception as e:
            logger.error(f"Failed to save final output: {e}")
    
    def _write_dataframe(self, df: pd.DataFrame, output_path: Path, output_format: str = 'csv'):
        """Write dataframe to file with proper formatting."""
        from config import CSV_CONFIG, TSV_CONFIG
        
        if output_format == 'tsv':
            config = TSV_CONFIG
        else:
            config = CSV_CONFIG
        
        # Map quoting options
        quoting_map = {
            'all': 1,        # csv.QUOTE_ALL
            'minimal': 0,    # csv.QUOTE_MINIMAL  
            'non_numeric': 2, # csv.QUOTE_NONNUMERIC
            'none': 3        # csv.QUOTE_NONE
        }
        
        quoting = quoting_map.get(config['quoting'], 0)
        
        df.to_csv(
            output_path,
            sep=config['delimiter'],
            quotechar=config['quotechar'],
            quoting=quoting,
            index=False,
            escapechar=config.get('escape_char') if config['quoting'] == 'none' else None
        )
    
    def _save_summary(self, df: pd.DataFrame, summary_path: Path):
        """Save processing summary."""
        try:
            total = len(df)
            completed = len(df[df.get('processing_status', '') == 'completed'])
            failed = len(df[df.get('processing_status', '') == 'failed'])
            
            summary = f"""Bookmark Processing Summary
============================
Total bookmarks: {total}
Successfully processed: {completed}
Failed: {failed}
Success rate: {(completed/total*100):.1f}%

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(summary_path, 'w') as f:
                f.write(summary)
                
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")