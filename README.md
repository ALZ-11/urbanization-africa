# Urbanization in Africa - Dynamic Geospatial Analysis

## Description
This platform provides a dynamic data pipeline and interactive analytics dashboard exploring urbanization, demographic trends, and transport logistics across the African continent. 

The project demonstrates dynamic data fusion and geospatial visualization by pulling live relational data from the Wikidata triple-store (via SPARQL) and merging it with macroeconomic indicators from the World Bank API.

## Live Dashboard
*   **Interactive Web App:** https://urbanization-africa.streamlit.app/

## Advanced Features
*   **Live SPARQL ETL Engine**: Python-driven query orchestration communicating directly with the Wikidata API with customized compliant User-Agent headers and local configuration loading.
*   **Decoupled SPARQL Files**: Multi-dimensional semantic queries decoupled into standalone `.sparql` files inside a queries registry module.
*   **Interactive GIS Mapping**: Mapbox OpenStreetMap scatter maps displaying city density, maritime ports, and aviation hubs color-coded by infrastructure type.
*   **Multi-Source Data Fusion**: Integration with the World Bank API to overlay city-level demographic data on top of national urbanization trajectories (`SP.URB.TOTL.IN.ZS`).
*   **Performance Telemetry**: Real-time pipeline latency tracking in the sidebar showing database access speeds and verifying local cache efficiency.
*   **Data Export**: CSV compilation allowing users to download any of the live-generated datasets with a single click.

## Project Structure
*   `src/`: Core Python modules managing extraction, configurations, and transformations.
    *   `src/queries/`: Decoupled standalone `.sparql` query files.
    *   `src/queries.py`: Helper module loading queries dynamically.
    *   `src/extract.py`: Direct network clients handling Wikidata and World Bank API requests.
    *   `src/transform.py`: Standardized dataset cleaning, datatype conversions, and parsing routines.
    *   `src/constants.py`: Dedicated configuration module containing static mapping datasets.
*   `tests/`: Automated test suite containing offline unit tests (`test_transform.py`).
*   `app.py`: Streamlit-based presentation layer managing interactive web components and Plotly charts.
*   `.env.example`: Configuration template for local developer credentials.

## Setup & Running the Project

### 1. Prerequisites & Environment Setup
Ensure you have Python installed. Clone this repository, set up your local environment file, and install the dependencies:

```bash
# Clone and enter the repository
git clone https://github.com/ALZ-11/urbanization-africa
cd urbanization-africa

# Create your local configuration file
cp .env.example .env
# Open '.env' in your text editor and add your email/github credentials

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Interactive App (Streamlit)
To launch the interactive dashboard locally:
```bash
streamlit run app.py
```

### 3. Run the Automated Test Suite
To execute the automated offline unit tests verifying your transformation and parsing calculations:
```bash
python -m unittest tests/test_transform.py
```
