#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests",
# ]
# ///

"""
Download Wisconsin Department of Revenue sales CSV files.

Usage:
    uvx download_wi_sales.py
    uvx download_wi_sales.py --path /custom/path
    uvx download_wi_sales.py --start-date 2020-01
"""

import argparse
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from io import BytesIO

import requests


BASE_URL = "https://www.revenue.wi.gov/SLFReportsHistSales"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Wisconsin sales CSV files"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.home() / "data" / "wi-sales",
        help="Directory to save CSV files (default: ~/data/wi-sales/)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2020-01",
        help="Start date in YYYY-MM format (default: 2020-01)",
    )
    return parser.parse_args()


def generate_months(start_date_str):
    """Generate YYYYMM strings from start_date to current month."""
    start_year, start_month = map(int, start_date_str.split("-"))
    now = datetime.now()
    
    current_year = start_year
    current_month = start_month
    
    while (current_year < now.year) or (current_year == now.year and current_month <= now.month):
        yield f"{current_year:04d}{current_month:02d}"
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1


def file_exists(url):
    """Check if a file exists at the given URL using HEAD request."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


def download_and_extract(url, target_path, filename):
    """Download ZIP file and extract CSV to target directory."""
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Extract CSV from ZIP in memory
        csv_filename = filename.replace(".zip", ".csv")
        csv_path = target_path / csv_filename
        
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            # Extract to temporary location
            csv_content = zip_file.read(csv_filename)
        
        # Convert to UTF-8
        # Try common encodings in order of likelihood
        for encoding in ['utf-8', 'cp1252', 'latin-1']:
            try:
                text = csv_content.decode(encoding)
                # Write as UTF-8
                csv_path.write_text(text, encoding='utf-8')
                print(f"✓ Saved {csv_filename} (converted from {encoding} to UTF-8)")
                return True
            except (UnicodeDecodeError, UnicodeError):
                if encoding == 'latin-1':
                    # latin-1 should never fail, so if we're here something is very wrong
                    raise
                continue
        
        return False
    except requests.RequestException as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False
    except zipfile.BadZipFile:
        print(f"✗ Invalid ZIP file: {filename}")
        return False
    except Exception as e:
        print(f"✗ Failed to process {filename}: {e}")
        return False


def download_csv_direct(url, target_path, filename):
    """Download CSV file directly (not from ZIP) and convert to UTF-8."""
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        csv_content = response.content
        csv_path = target_path / filename
        
        # Convert to UTF-8
        # Try common encodings in order of likelihood
        for encoding in ['utf-8', 'cp1252', 'latin-1']:
            try:
                text = csv_content.decode(encoding)
                # Write as UTF-8
                csv_path.write_text(text, encoding='utf-8')
                print(f"✓ Saved {filename} (converted from {encoding} to UTF-8)")
                return True
            except (UnicodeDecodeError, UnicodeError):
                if encoding == 'latin-1':
                    # latin-1 should never fail, so if we're here something is very wrong
                    raise
                continue
        
        return False
    except requests.RequestException as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to process {filename}: {e}")
        return False


def main():
    args = parse_args()
    
    # Create target directory if it doesn't exist
    args.path.mkdir(parents=True, exist_ok=True)
    
    print(f"Target directory: {args.path}")
    print(f"Starting from: {args.start_date}")
    print()
    
    # Get existing CSV files
    existing_files = {f.stem for f in args.path.glob("*.csv")}
    
    downloaded = 0
    skipped = 0
    consecutive_404s = 0
    max_consecutive_404s = 3  # Stop after 3 consecutive missing files
    
    for month in generate_months(args.start_date):
        filename = f"{month}CSV"
        csv_name = f"{filename}.csv"
        
        # Skip if CSV already exists
        if filename in existing_files:
            print(f"⊘ Skipping {csv_name} (already exists)")
            skipped += 1
            continue
        
        # First, check if ZIP exists on server
        zip_url = f"{BASE_URL}/{filename}.zip"
        csv_url = f"{BASE_URL}/{csv_name}"
        
        if file_exists(zip_url):
            # Reset consecutive 404 counter if we found a file
            consecutive_404s = 0
            
            # Download and extract ZIP
            if download_and_extract(zip_url, args.path, f"{filename}.zip"):
                downloaded += 1
        elif file_exists(csv_url):
            # Reset consecutive 404 counter if we found a file
            consecutive_404s = 0
            
            # Download CSV directly
            if download_csv_direct(csv_url, args.path, csv_name):
                downloaded += 1
        else:
            # Neither ZIP nor CSV found
            consecutive_404s += 1
            print(f"⊘ {filename} not found (tried .zip and .csv)")
            
            if consecutive_404s >= max_consecutive_404s:
                print(f"\nStopping after {max_consecutive_404s} consecutive missing files.")
                break
    
    print()
    print(f"Summary: {downloaded} downloaded, {skipped} skipped")


if __name__ == "__main__":
    main()
