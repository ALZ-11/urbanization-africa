# Urbanization in Africa - Big Data Analysis

## Description
This project focuses on analyzing urbanization trends and infrastructure in Africa. It uses live SPARQL queries to extract data dynamically from Wikidata and Python for data analysis and visualization.

## Live Dashboard
*   **Interactive Web App:** https://urbanization-africa.streamlit.app/

## Project Structure
- `data/`: (Optional) Directory reserved for local data caching or offline layers.
- `notebooks/`: Exploratory data analysis notebook (`visualisations.ipynb`).
- `docs/`: Reference documentation, SPARQL queries (`requetes_SPARQL.txt`), and static outputs.
- `app.py`: Streamlit-based presentation layer for interactive web analysis.
- `src/`: Source code including the data extraction engine.

## Setup & Running the Project

### 1. Prerequisites & Environment Setup
Ensure you have Python installed. Clone this repository, set up your local environment file, and install the dependencies:

```bash
# Clone and enter the repository
git clone https://github.com/ALZ-11/urbanization-africa.git
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

### 3. Run the Exploratory Notebook
To open and run the Jupyter notebook locally:
```bash
jupyter notebook notebooks/visualisations.ipynb
```
