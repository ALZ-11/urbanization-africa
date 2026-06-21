import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extract import WikidataExtractor

extractor = WikidataExtractor()

test_query = """
SELECT ?countryLabel WHERE {
  ?country wdt:P30 wd:Q15. # Africa
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
LIMIT 5
"""

df = extractor.fetch_data(test_query)
print("\nTest Results:")
print(df)