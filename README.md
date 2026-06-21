# Urbanization in Africa - Big Data Analysis

## Description
This project focuses on analyzing urbanization trends and infrastructure in Africa. It uses SPARQL queries to extract data from Wikidata and Python for data analysis and visualization.

## Project Structure
- `data/`: Contains the cached static datasets extracted from Wikidata.
- `notebooks/`: Exploratory data analysis notebook (`visualisations.ipynb`).
- `docs/`: Reference documentation, SPARQL queries (`requetes_SPARQL.txt`), and static outputs.
- `app.py`: Streamlit-based presentation layer for interactive web analysis.

## Setup & Running the Project

### 1. Prerequisites
Ensure you have Python installed. Clone this repository and install the dependencies:
```bash
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
