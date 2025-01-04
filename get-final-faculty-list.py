import os
import csv
import logging
from bs4 import BeautifulSoup
import re
from datetime import datetime


# Set up logging
def setup_logging(log_dir='logs'):
    """Configure logging with both file and console handlers."""
    os.makedirs(log_dir, exist_ok=True)

    # Create a timestamp for the log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'dblp_parser_{timestamp}.log')

    # Configure logging format
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # Set up root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info('Starting DBLP HTML parser')


def extract_scholar_id(html):
    """
    Try to extract Google Scholar ID from links in the HTML.
    Returns None if not found.
    """
    # Look for Google Scholar links which typically contain the ID
    scholar_links = html.find_all('a', href=re.compile(r'scholar\.google\.com'))
    for link in scholar_links:
        href = link.get('href', '')
        match = re.search(r'user=([^&]+)', href)
        if match:
            return match.group(1)
    return None


def extract_homepage(html, filename=None):
    """
    Try to extract homepage URL from the HTML. Uses the following priority:
    1. Homepage link from 'visit' section if available
    2. DBLP persistent URL as fallback
    Returns None if neither is found.
    """
    # First try to get homepage from visit section
    visit_section = html.find('li', class_='visit')
    if visit_section:
        link = visit_section.find('a')
        if link:
            homepage = link.get('href')
            logging.info(f"Found homepage in visit section: {homepage}")
            return homepage

    # If no homepage in visit section, get the DBLP persistent URL
    share_section = html.find('li', class_='share')
    if share_section:
        # The persistent URL is in a bullets list within the share dropdown
        bullets = share_section.find('ul', class_='bullets')
        if bullets:
            persistent_link = bullets.find('a')
            if persistent_link:
                dblp_url = persistent_link.get_text().strip()
                logging.info(f"Using DBLP URL as homepage: {dblp_url}")
                return dblp_url

    logging.warning(f"No homepage or DBLP URL found for {filename}")
    return None


def parse_dblp_html(html_content, filename=None):
    """
    Parse DBLP HTML content and extract required fields.
    Returns a dictionary with name, homepage, and scholarid.
    Note: affiliation is handled at the directory level, not from HTML content.
    """
    logging.debug(f'Parsing HTML content for {filename if filename else "unknown file"}')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract name - it's in the h1 tag with class 'name primary'
    name_elem = soup.find('span', class_='name primary')
    name = name_elem.get_text().strip() if name_elem else None

    # Extract homepage
    homepage = extract_homepage(soup)

    # Extract Google Scholar ID
    scholar_id = extract_scholar_id(soup)

    return {
        'name': name,
        'affiliation': None,  # Will be set based on directory name
        'homepage': homepage,
        'scholarid': scholar_id
    }


def process_dblp_files(base_dir, output_file):
    """
    Process all HTML files in subdirectories of base_dir and write results to output_file.
    Uses the directory name as the affiliation.
    """
    logging.info(f'Starting to process files from {base_dir}')
    logging.info(f'Output will be written to {output_file}')
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write header and process files
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'affiliation', 'homepage', 'scholarid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each university directory
        for univ_dir in os.listdir(base_dir):
            univ_path = os.path.join(base_dir, univ_dir)
            if not os.path.isdir(univ_path):
                continue

            # Convert directory name to university name (e.g., "harvard" -> "Harvard University")
            university = " ".join(word.capitalize() for word in univ_dir.split('_'))
            if not university.lower().endswith(('university', 'institute', 'college')):
                university += " University"

            # Process each HTML file in the university directory
            for filename in os.listdir(univ_path):
                if filename.endswith('.html'):
                    file_path = os.path.join(univ_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as htmlfile:
                            html_content = htmlfile.read()
                            result = parse_dblp_html(html_content, filename)
                            if result['name']:  # Only write if we found a name
                                result['affiliation'] = university
                                writer.writerow(result)
                                logging.info(f"Processed {filename} from {university}: {result['name']}")
                            else:
                                logging.warning(f"No name found in {filename} from {university}")
                    except Exception as e:
                        logging.error(f"Error processing {university}/{filename}: {str(e)}", exc_info=True)


def main():
    # Set up logging
    setup_logging()

    try:
        base_directory = "faculty_html"  # Base directory containing university subdirectories
        output_csv = "output/faculty_data.csv"

        # Log script start
        logging.info("Starting DBLP faculty parser script")
        logging.info(f"Base directory: {base_directory}")
        logging.info(f"Output file: {output_csv}")

        # Process files
        process_dblp_files(base_directory, output_csv)

        # Log completion
        logging.info("Script completed successfully")
    except Exception as e:
        logging.error("Script failed with error", exc_info=True)
        raise


if __name__ == "__main__":
    main()