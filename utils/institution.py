from pydantic import BaseModel, Field
from typing import List, Optional # Keep Optional for better type hints
import requests
from bs4 import BeautifulSoup
import re # Import regex for better string cleaning

# Define InstitutionDetails Schema
class InstitutionDetails(BaseModel):
    name: str = Field(description="Institution name")
    founder: str = Field(description="Founder's name")
    founded_year: str = Field(description="Year founded")
    branches: List[str] = Field(description="List of branches")
    employees: str = Field(description="Approx. employee count")
    summary: str = Field(description="4-line summary")

# Placeholder for a function that would scrape Wikipedia
def fetch_from_wikipedia(institution_name: str) -> Optional[InstitutionDetails]:
    print(f"Attempting to fetch data for '{institution_name}' from Wikipedia...")
    
    # Normalize the search term for Wikipedia URL: replace spaces with underscores, handle special chars
    # Wikipedia URLs are case-sensitive to some extent, but often a capitalized first letter works best.
    # For robust search, you'd ideally use Wikipedia's API to get the canonical page title.
    # For now, we'll try a simple title-case conversion and then underscore spaces.
    
    # Attempt to convert to a common Wikipedia title format
    # Simple capitalization for each word after cleaning.
    normalized_search_term = " ".join([word.capitalize() for word in institution_name.split()])
    
    # Handle specific common abbreviations/names if they have direct Wikipedia pages
    # This is a very basic example; a real system would need a more comprehensive mapping.
    if normalized_search_term.upper() == "JNU":
        normalized_search_term = "Jawaharlal_Nehru_University" # Direct to specific page
    elif normalized_search_term.upper() == "IIT BOMBAY":
        normalized_search_term = "Indian_Institute_of_Technology_Bombay"
    elif normalized_search_term.upper() == "AIIMS DELHI":
        normalized_search_term = "All_India_Institute_of_Medical_Sciences,_Delhi"
    # Add more such mappings as needed

    wikipedia_url = f"https://en.wikipedia.org/wiki/{normalized_search_term.replace(' ', '_')}"

    try:
        response = requests.get(wikipedia_url, timeout=10) # Added timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if it's a disambiguation page
        # Disambiguation pages often have a "This article is about..." or "disambiguation" class
        if soup.find(id='disambigbox') or "disambiguation" in soup.title.text.lower():
            print(f"'{institution_name}' led to a disambiguation page: {wikipedia_url}")
            # In a real scenario, you'd parse the disambiguation page to find the correct link
            # or try a more specific search query. For now, we'll return None.
            return None 
            
        found_name = institution_name # Default to input name
        found_founder = "Not Available"
        found_founded_year = "Not Available"
        found_branches = []
        found_employees = "Not Available"
        found_summary = "No summary found."

        # Attempt to find infobox (common for institution details)
        infobox = soup.find('table', class_='infobox')
        
        if infobox:
            for row in infobox.find_all('tr'):
                header = row.find('th')
                data = row.find('td')
                if header and data:
                    header_text = header.get_text(strip=True)
                    data_text = data.get_text(strip=True)
                    
                    if "Founder" in header_text:
                        found_founder = data_text
                    elif "Established" in header_text or "Founded" in header_text:
                        # Extract just the year if there are multiple dates or text
                        match = re.search(r'\b\d{4}\b', data_text)
                        if match:
                            found_founded_year = match.group(0)
                        else:
                            found_founded_year = data_text
                    elif "Campus" in header_text or "Location" in header_text or "Branches" in header_text:
                        # Split by common delimiters
                        branches_raw = data_text.split(',')
                        found_branches.extend([b.strip() for b in branches_raw if b.strip() and "Campus" not in b]) # Basic filter
                    elif "Employees" in header_text or "Staff" in header_text:
                        found_employees = data_text
                    elif "President" in header_text or "Director" in header_text:
                        # This could be used for key people, but schema doesn't have it directly from infobox here
                        pass
        
        # Attempt to get a summary (first few paragraphs)
        paragraphs = soup.find_all('p')
        summary_lines = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out common Wikipedia navigation/disclaimer paragraphs
            if text and not text.startswith("Coordinates:") and not "For other uses," in text and not "From Wikipedia, the free encyclopedia" in text:
                summary_lines.append(text)
            if len(summary_lines) >= 4: # Aim for 4 lines of summary
                break
        
        found_summary = "\n".join(summary_lines[:4]) if summary_lines else "No summary found."
        
        # Ensure name is the actual official name from the Wikipedia page if available (e.g., from page title or infobox)
        # This is often the primary H1 tag
        h1_title = soup.find('h1', id='firstHeading')
        if h1_title:
            found_name = h1_title.get_text(strip=True)

        return InstitutionDetails(
            name=found_name,
            founder=found_founder,
            founded_year=found_founded_year,
            branches=list(set(found_branches)), # Remove duplicates
            employees=found_employees,
            summary=found_summary
        )

    except requests.exceptions.Timeout:
        print(f"Timeout fetching data from Wikipedia for {institution_name}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP error fetching data from Wikipedia for {institution_name}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during scraping for {institution_name}: {e}")
        return None

# Hardcoded data as a fallback (made some details more robust based on typical info)
HARDCODED_INSTITUTION_DATA = {
    "Indian Institute of Technology Bombay": InstitutionDetails(
        name="Indian Institute of Technology Bombay",
        founder="Dr. Bhabha",
        founded_year="1958",
        branches=["Mumbai"], # Often just one main campus for IITs officially
        employees="5000+",
        summary=(
            "The Indian Institute of Technology Bombay (IIT Bombay) is one of India's most prestigious engineering and research institutions, established in 1958. "
            "Located in Powai, Mumbai, its sprawling campus is a hub of academic excellence and innovation. IIT Bombay is consistently ranked among the top technical universities "
            "in India and globally, attracting brilliant minds from across the country. It offers a wide array of undergraduate, postgraduate, and doctoral programs in engineering, "
            "science, humanities, and management."
        )
    ),
    "Indian Institute of Science": InstitutionDetails(
        name="Indian Institute of Science",
        founder="Jamsetji Tata",
        founded_year="1909",
        branches=["Bengaluru"],
        employees="3000+",
        summary=(
            "The Indian Institute of Science (IISc), located in Bengaluru, is India's premier institution for advanced scientific and technological research and education. "
            "It was established in 1909 with the visionary support of Jamsetji Tata and the then Maharaja of Mysore, becoming a cornerstone of India's scientific progress. "
            "IISc is internationally recognized for its rigorous academic programs, pioneering research, and significant contributions to fundamental and applied sciences. "
            "The institute offers a wide range of master's and doctoral programs in various disciplines."
        )
    ),
    "All India Institute of Medical Sciences, Delhi": InstitutionDetails( # Full name for consistency
        name="All India Institute of Medical Sciences, Delhi",
        founder="Government of India",
        founded_year="1956",
        branches=["New Delhi"], # Main campus
        employees="10000+",
        summary=(
            "The All India Institute of Medical Sciences, New Delhi (AIIMS Delhi) stands as India's leading medical institution, established in 1956 by the Government of India. "
            "It operates as a public medical research university and hospital, setting national benchmarks for medical education, research, and patient care. "
            "AIIMS Delhi is consistently ranked as the top medical college in the country, renowned for its highly specialized clinical services and advanced research facilities. "
            "It offers comprehensive undergraduate and postgraduate medical and paramedical courses."
        )
    ),
    "Jawaharlal Nehru University": InstitutionDetails( # Full name for JNU
        name="Jawaharlal Nehru University",
        founder="Government of India",
        founded_year="1969",
        branches=["New Delhi"],
        employees="1200+",
        summary=(
            "Jawaharlal Nehru University (JNU) is a public central university located in New Delhi, India. "
            "It was established in 1969 and is known for its liberal arts and social science programs. "
            "JNU is one of the leading universities in India, recognized for its research in various fields. "
            "It attracts students and faculty from across the globe."
        )
    ),
    "Stanford University": InstitutionDetails(
        name="Stanford University",
        founder="Leland Stanford, Jane Stanford",
        founded_year="1885",
        branches=["Stanford, California"],
        employees="20000+",
        summary=(
            "Stanford University, officially Leland Stanford Junior University, is a private research university in Stanford, California. "
            "It was founded in 1885 by Leland and Jane Stanford in memory of their son, Leland Stanford Jr. "
            "The university is known for its academic excellence, research, and proximity to Silicon Valley, fostering innovation and entrepreneurship. "
            "It offers programs in a wide range of disciplines."
        )
    ),
    "Massachusetts Institute of Technology": InstitutionDetails(
        name="Massachusetts Institute of Technology",
        founder="William Barton Rogers",
        founded_year="1861",
        branches=["Cambridge, Massachusetts"],
        employees="12000+",
        summary=(
            "The Massachusetts Institute of Technology (MIT) is a private land-grant research university in Cambridge, Massachusetts. "
            "Established in 1861, MIT is known for its cutting-edge research and education in science, engineering, and technology. "
            "It has played a key role in the development of modern technology and scientific advancements. "
            "MIT consistently ranks among the world's top universities."
        )
    )
}

# Modified get_institution_info to try fetching from web first, then fallback to hardcoded
def get_institution_info(institution_name: str) -> InstitutionDetails:
    # Normalize input name for consistent lookup in hardcoded data and for potential display
    normalized_input_name = " ".join([word.capitalize() for word in institution_name.split()])

    # Step 1: Try to fetch from Wikipedia
    try:
        wiki_details = fetch_from_wikipedia(normalized_input_name)
        if wiki_details:
            # Check for minimal data extracted from Wikipedia
            if wiki_details.summary != "No summary found." and wiki_details.founded_year != "Not Available":
                print(f"Successfully fetched data for '{institution_name}' from Wikipedia.")
                return wiki_details
            else:
                print(f"Wikipedia data for '{institution_name}' was incomplete, attempting fallback.")
    except ValueError as e:
        print(f"Error during Wikipedia fetch: {e}. Attempting fallback.")
    
    # Step 2: Fallback to hardcoded data
    # We'll try to match the normalized input name to keys in hardcoded data
    if normalized_input_name in HARDCODED_INSTITUTION_DATA:
        print(f"Falling back to hardcoded data for '{institution_name}'.")
        return HARDCODED_INSTITUTION_DATA[normalized_input_name]
    
    # Step 3: Check for common aliases/variations in hardcoded data keys
    # This loop allows for flexible matching against hardcoded keys
    for key, details in HARDCODED_INSTITUTION_DATA.items():
        if normalized_input_name.lower() == key.lower() or \
           normalized_input_name.lower() in key.lower(): # e.g., "IIT Bombay" matches "Indian Institute of Technology Bombay"
            print(f"Falling back to hardcoded data using alias match for '{institution_name}' (matched with '{key}').")
            return details

    raise ValueError(f"No data available for '{institution_name}' from web or hardcoded sources.")


# Example Usage
if __name__ == "__main__":
    print("--- Testing get_institution_info ---")

    # Test with varying cases
    test_institutions = [
        "indian institute of science", # lower case
        "Indian Institute of Science", # Title Case
        "INDIAN INSTITUTE OF SCIENCE", # UPPER CASE
        "iit bombay",                 # lower case abbreviation
        "IIT BOMBAY",                 # UPPER CASE abbreviation
        "Stanford University",
        "MASSACHUSETTS INSTITUTE OF TECHNOLOGY",
        "jnu",                        # lower case abbreviation
        "University of Gondor",       # Fictional, should error
        "Fictional University of Nowhere ABCDEFG" # Truly non-existent, should error
    ]

    for inst_name in test_institutions:
        print(f"\n--- Fetching: {inst_name} ---")
        try:
            result = get_institution_info(inst_name)
            print(f"Summary Length: {len(result.summary.splitlines())} lines")
            print(result.json(indent=2))
        except ValueError as e:
            print(f"Error: {e}")