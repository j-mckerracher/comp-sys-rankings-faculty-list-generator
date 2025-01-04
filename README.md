# Faculty Data Collection Project

This project is designed to collect and process academic faculty data from DBLP (Digital Bibliography & Library Project), creating a comprehensive dataset of university faculty members with their associated metadata.

## Project Overview

The system operates in three main stages:

1. Initial data collection from DBLP's SPARQL endpoint
2. HTML page retrieval for individual faculty members
3. Final data extraction and standardization

## Components

### 1. get-faculty-csv-from-dblp.py

This script performs the initial data collection phase:

- Queries DBLP's SPARQL endpoint to find faculty members associated with specific universities
- Processes a list of US universities from the 'us-schools' input file
- Implements rate limiting and retry logic to handle API restrictions
- Saves results in CSV format under the `faculty_data` directory
- Creates a 'fails' file listing universities that couldn't be processed

Usage:
```bash
python get-faculty-csv-from-dblp.py
```

Required input:
- `us-schools`: Text file containing list of universities to process

Output:
- `faculty_data/*.csv`: CSV files containing faculty data for each university
- `fails`: List of universities that failed processing

### 2. get-dblp-faculty-html.py

This script handles the second phase of data collection:

- Reads the CSV files generated in the first phase
- Downloads individual DBLP pages for each faculty member
- Implements robust error handling and rate limiting
- Organizes downloaded HTML files by university
- Includes logging functionality for tracking progress and debugging

Usage:
```bash
python get-dblp-faculty-html.py
```

Required input:
- `faculty_data` directory containing CSV files from phase 1

Output:
- `faculty_html/<university>/*.html`: HTML files for each faculty member
- `faculty_scraper.log`: Detailed logging information

### 3. get-final-faculty-list.py

This script performs the final data processing phase:

- Parses downloaded HTML files to extract structured information
- Collects faculty names, affiliations, homepages, and Google Scholar IDs
- Standardizes university names and data formats
- Implements comprehensive logging for tracking and debugging
- Produces a final consolidated CSV file with all faculty information

Usage:
```bash
python get-final-faculty-list.py
```

Required input:
- `faculty_html` directory containing downloaded HTML files

Output:
- `output/faculty_data.csv`: Final consolidated faculty dataset
- `logs/dblp_parser_*.log`: Timestamped log files

## Setup and Dependencies

Required Python packages:
- requests
- pandas
- beautifulsoup4
- logging

Install dependencies:
```bash
pip install requests pandas beautifulsoup4
```

## Directory Structure

```
.
├── faculty_data/           # Initial CSV files from SPARQL queries
├── faculty_html/          # Downloaded HTML pages organized by university
├── output/               # Final processed data
├── logs/                # Script execution logs
└── scripts
    ├── get-faculty-csv-from-dblp.py
    ├── get-dblp-faculty-html.py
    └── get-final-faculty-list.py
```

## Error Handling and Logging

The project implements comprehensive error handling and logging throughout:

- All scripts include detailed logging configurations
- Failed operations are tracked and reported
- Rate limiting is implemented to respect API restrictions
- Retry logic is included for handling temporary failures
- Errors are logged with timestamps and full stack traces when appropriate

## Best Practices

When running this project:

1. Ensure adequate disk space for HTML storage
2. Respect DBLP's rate limits and terms of service
3. Monitor log files for potential issues
4. Back up the `faculty_data` directory before running updates
5. Consider running scripts during off-peak hours for better performance

## Data Fields

The final output CSV includes the following fields:
- name: Faculty member's full name
- affiliation: University affiliation
- homepage: Personal or institutional homepage URL
- scholarid: Google Scholar ID (when available)