# src/extract.py
import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikidataExtractor:
    """Handles data extraction from the Wikidata SPARQL endpoint"""
    
    ENDPOINT_URL = "https://query.wikidata.org/sparql"
    
    def __init__(self):
        email = os.getenv("CONTACT_EMAIL", "developer@example.com")
        github = os.getenv("GITHUB_USERNAME", "anonymous-developer")
        
        self.headers = {
            'User-Agent': f'AfricanUrbanizationBot/1.0 (https://github.com/{github}; mailto:{email})'
        }

    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Executes a SPARQL query and parses the JSON response into a flat Pandas DataFrame.
        """
        logging.info("Sending query to Wikidata endpoint...")
        try:
            response = requests.get(
                self.ENDPOINT_URL, 
                params={'format': 'json', 'query': query},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            results = data['results']['bindings']
            rows = []
            for item in results:
                row = {key: val['value'] for key, val in item.items()}
                rows.append(row)
                
            logging.info(f"Successfully retrieved {len(rows)} records.")
            return pd.DataFrame(rows)
            
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logging.error(f"An unexpected error occurred during extraction: {err}")
            
        return pd.DataFrame()