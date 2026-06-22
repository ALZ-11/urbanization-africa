# src/extract.py
import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikidataExtractor:
    ENDPOINT_URL = "https://query.wikidata.org/sparql"
    
    def __init__(self):
        email = os.getenv("CONTACT_EMAIL", "developer@example.com")
        github = os.getenv("GITHUB_USERNAME", "anonymous-developer")
        self.headers = {
            'User-Agent': f'AfricanUrbanizationBot/1.0 (https://github.com/{github}; mailto:{email})'
        }

    def fetch_data(self, query: str) -> pd.DataFrame:
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

class WorldBankExtractor:
    BASE_URL = "http://api.worldbank.org/v2/country"
    
    def fetch_urban_data(self, country_code: str) -> list:
        url = f"{self.BASE_URL}/{country_code}/indicator/SP.URB.TOTL.IN.ZS"
        params = {"format": "json", "date": "1970:2025"}
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to fetch data from World Bank API: {e}")
            return []