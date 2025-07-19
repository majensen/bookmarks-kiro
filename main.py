#!/usr/bin/env python3
"""
Bookmark Enrichment Tool
Processes CSV bookmark exports and enriches them with AI-generated summaries and tags.
"""

import sys
import argparse
from pathlib import Path

from src.bookmark_processor import BookmarkProcessor
from src.utils import setup_logging

def main():
    parser = argparse.ArgumentParser(description='Enrich bookmarks with AI-generated summaries and tags')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--output', '-o', help='Output file path (default: input_file_enriched.csv/tsv)')
    parser.add_argument('--format', '-f', choices=['csv', 'tsv'], default='csv', help='Output format: csv or tsv (default: csv)')
    parser.add_argument('--resume', '-r', action='store_true', help='Resume from previous run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        extension = '.tsv' if args.format == 'tsv' else '.csv'
        output_path = input_path.parent / f"{input_path.stem}_enriched{extension}"
    
    # Process bookmarks
    processor = BookmarkProcessor()
    processor.process_file(input_path, output_path, output_format=args.format, resume=args.resume)
    
    print(f"Processing complete. Enriched bookmarks saved to: {output_path}")

if __name__ == '__main__':
    main()