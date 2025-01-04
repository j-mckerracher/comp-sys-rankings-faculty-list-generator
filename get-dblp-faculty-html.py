import requests
import csv
import time
import logging
from pathlib import Path
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faculty_scraper.log'),
        logging.StreamHandler()
    ]
)


def setup_directories():
    """Create necessary directories if they don't exist."""
    faculty_data_dir = Path('faculty_data')
    faculty_html_dir = Path('faculty_html')

    if not faculty_data_dir.exists():
        logging.error(f"Directory {faculty_data_dir} not found. Please run get-faculty-csv-from-dblp.py first.")
        return False

    faculty_html_dir.mkdir(exist_ok=True)
    return True


def get_dblp_page(url, retry_delay=5, max_retries=3):
    """
    Download a DBLP page with rate limiting and retries.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Academic Research Bot; +https://example.org/bot)'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 429:  # Too Many Requests
                logging.warning(f"Rate limit hit. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue

            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {url} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    return None


def process_faculty_file(csv_path, faculty_html_dir):
    """
    Process a single faculty CSV file and download DBLP pages.
    """
    university_name = csv_path.stem.replace('_faculty', '')
    logging.info(f"Processing faculty from: {university_name}")

    # Create university-specific subdirectory
    univ_dir = faculty_html_dir / university_name
    univ_dir.mkdir(exist_ok=True)

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dblp_url = row['author'].strip()
                if not dblp_url:
                    continue

                # Create a safe filename from the DBLP URL
                parsed_url = urlparse(dblp_url)
                safe_filename = parsed_url.path.replace('/', '_').strip('_') + '.html'
                output_path = univ_dir / safe_filename

                # Skip if already downloaded
                if output_path.exists():
                    logging.info(f"Skipping {dblp_url} - already downloaded")
                    continue

                logging.info(f"Downloading {dblp_url}")
                html_content = get_dblp_page(dblp_url)

                if html_content:
                    output_path.write_text(html_content, encoding='utf-8')
                    time.sleep(1)  # Rate limiting between requests

    except Exception as e:
        logging.error(f"Error processing {csv_path}: {e}")


def main():
    """
    Main function to coordinate the downloading of faculty DBLP pages.
    """
    if not setup_directories():
        return

    faculty_data_dir = Path('faculty_data')
    faculty_html_dir = Path('faculty_html')

    # Process each CSV file in the faculty_data directory
    csv_files = list(faculty_data_dir.glob('*_faculty.csv'))

    if not csv_files:
        logging.error("No faculty CSV files found in faculty_data directory")
        return

    logging.info(f"Found {len(csv_files)} faculty CSV files to process")

    for csv_file in csv_files:
        process_faculty_file(csv_file, faculty_html_dir)
        time.sleep(2)  # Add delay between processing different universities

    logging.info("Completed downloading faculty DBLP pages")


if __name__ == "__main__":
    main()
    main()