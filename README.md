# MQL5 Data Parser CLI

A monolithic, robust Command Line Interface (CLI) tool written in Python to automatically clean, parse, and format CSV data exports from MetaTrader 5 (MQL5). 

It intelligently detects whether the input file contains **Bar Data (OHLCV)** or **Tick Data**, normalizes timestamps, handles missing values, and overwrites files with clean data ready for algorithmic trading, backtesting, or quantitative analysis.

## Features

- **Auto-Detection:** Automatically detects file structure (Bars vs. Ticks) and adjusts processing logic.
- **Robust Delimiter Sensing:** Automatically handles both tab-separated (`\t`) and comma-separated (`,`) CSV files.
- **Smart Data Filling for Ticks:** Applies Forward-Fill (`ffill`) and Backward-Fill (`bfill`) on tick updates to prevent data loss.
- **Dynamic Empty Column Cleanup:** Instantly drops columns that are 100% empty (like an unused `Last` column from specific brokers) instead of breaking the row count.
- **Batch Processing:** Processes single files, a manual list of multiple files, or wildcards (e.g., `*.csv`).
- **Flexible Filtering:** Optional CLI flags to explicitly keep or drop specific columns.
- **Fault Tolerance:** Wrapped in global exception blocks—one corrupted file won't halt batch processing.

## Installation

1. Clone or download this repository to your local machine.
2. Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
Usage
Run the script from your terminal by passing the paths to your exported MQL5 CSV files.

1. Basic Processing (Auto-detect & Clean)
To process a single file:

Bash
python mql_parser.py eth.csv
To process multiple specific files sequentially:

Bash
python mql_parser.py eth.csv btc.csv sol_ticks.csv
To batch-process every single CSV file in the current directory:

Bash
python mql_parser.py *.csv
2. Advanced Column Filtering
By default, the script keeps all columns that contain data (dropping only standard metadata junk like Vol or Spread for bars, and Flags for ticks). You can override this using mutually exclusive flags:

Keep only specific columns (in addition to baseline OHLCV or Bid/Ask/Last):

Bash
python mql_parser.py market_data.csv --keep spread flags
Force drop specific columns:

Bash
python mql_parser.py market_data.csv --drop volume
3. Display Help Menu
To view all available command-line options and syntax arguments:

Bash
python mql_parser.py --help
Internal Data Pipeline
Format Validation: Ensures <DATE> and <TIME> headers exist.

Index Alignment: Combines date and time columns into a unified, high-precision DateTime index.

Header Sanitization: Strips brackets (<, >) and capitalizes column titles (e.g., <BID> becomes Bid).

Volume Normalization: Maps MT5's Tickvol header to standard Volume.

Missing Value Handling: - For Bars: Drops rows containing incomplete metrics.

For Ticks: Automatically forward-fills and backward-fills gaps in market depth data.