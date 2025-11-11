# Wisconsin Sales Data Downloader

A simple Python script to download historical sales CSV files from the Wisconsin Department of Revenue.

## Prerequisites

This script requires [uv](https://docs.astral.sh/uv/) to be installed.

**Install uv:**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## Usage

Run directly from this repository:

```bash
uvx https://raw.githubusercontent.com/bnoffke/wi-real-estate-transactions-downloader/main/wi_sales_downloader.py
```

Or download and run locally:

```bash
# Download the script
curl -O https://raw.githubusercontent.com/bnoffke/wi-real-estate-transactions-downloader/main/wi_sales_downloader.py

# Run it
uvx wi_sales_downloader.py
```

## Options

```bash
# Download to default location (~/data/wi-sales/)
uvx wi_sales_downloader.py

# Specify custom directory
uvx wi_sales_downloader.py --path /path/to/save

# Start from a different date (default: 2020-01)
uvx wi_sales_downloader.py --start-date 2018-01

# Combine options
uvx wi_sales_downloader.py --path ./data --start-date 2019-06
```

## What it does

1. Checks for available sales data files at https://www.revenue.wi.gov/SLFReportsHistSales/
2. Downloads only the files that don't already exist in your target directory
3. Automatically extracts CSV files from ZIP archives
4. Saves CSV files with format `YYYYMMCSV.csv` (e.g., `202001CSV.csv`)

## Example Output

```
Target directory: /Users/you/data/wi-sales
Starting from: 2020-01

⊘ Skipping 202001CSV.csv (already exists)
Downloading 202002CSV...
✓ Saved 202002CSV.csv
Downloading 202003CSV...
✓ Saved 202003CSV.csv
⊘ 202004CSV.zip not found

Summary: 2 downloaded, 1 skipped
```
