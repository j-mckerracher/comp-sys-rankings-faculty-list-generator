import requests
import pandas as pd
import time
from pathlib import Path


def normalize_university_name(name):
    """Standardize university name format."""
    return name.strip().lower()


def query_dblp_sparql(query, retry_delay=5, max_retries=3):
    """Execute a SPARQL query against the DBLP endpoint with rate limiting."""
    endpoint = "https://sparql.dblp.org/sparql"
    headers = {
        'Accept': 'text/csv',
        'Content-Type': 'application/sparql-query'
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, data=query)

            if response.status_code == 429:  # Too Many Requests
                print(f"Rate limit hit. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue

            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Error making request (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    return None


def get_faculty_query(university):
    """Generate SPARQL query for a given university."""
    return f"""
    PREFIX dblp: <https://dblp.org/rdf/schema#>
    PREFIX schema: <https://schema.org/>
    SELECT ?author ?affiliation
    WHERE {{
        ?author dblp:primaryAffiliation ?affiliation .
        FILTER(CONTAINS(LCASE(?affiliation), "{university}"))
    }}
    """


def process_university(university, output_dir):
    """Query and save faculty data for a single university."""
    university_name = normalize_university_name(university)
    query = get_faculty_query(university_name)

    print(f"Querying faculty for: {university}")
    results = query_dblp_sparql(query)

    if results:
        # Create safe filename from university name
        safe_name = "".join(c if c.isalnum() else "_" for c in university_name)
        output_file = output_dir / f"{safe_name}_faculty.csv"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Saved results to {output_file}")
        return True

    print(f"Failed to get results for {university}")
    return False


def main():
    # Create output directory
    output_dir = Path('faculty_data')
    output_dir.mkdir(exist_ok=True)

    failed_schools = []

    # Read universities file
    try:
        with open('us-schools', 'r', encoding='utf-8') as f:
            universities = f.readlines()
    except FileNotFoundError:
        print("Error: 'us-schools' file not found")
        return

    # Process each university with delay between requests
    delay_between_universities = 2  # seconds

    for i, university in enumerate(universities, 1):
        print(f"\nProcessing university {i}/{len(universities)}")
        success = process_university(university, output_dir)

        if not success:
            failed_schools.append(university.strip())

        # Only delay if it's not the last university and the query was successful
        if i < len(universities) and success:
            print(f"Waiting {delay_between_universities} seconds before next query...")
            time.sleep(delay_between_universities)

    # Write failed schools to file
    if failed_schools:
        with open('fails', 'w', encoding='utf-8') as f:
            f.write('\n'.join(failed_schools))


if __name__ == "__main__":
    main()