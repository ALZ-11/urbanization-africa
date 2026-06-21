import streamlit as st
import pandas as pd
import plotly.express as px
from src.extract import WikidataExtractor

st.set_page_config(layout="wide", page_title="Urbanisation en Afrique")

st.title("Big Data et Urbanisation en Afrique")
st.markdown("""
Analyse exploratoire des dynamiques urbaines et infrastructures routières africaines. 
Données extraites en temps réel de **Wikidata** via des requêtes **SPARQL**.
""")

CITIES_QUERY = """
SELECT ?cityLabel ?countryLabel ?population WHERE {
  ?city wdt:P31 wd:Q515;        # Ville
        wdt:P17 ?country;       # Pays
        wdt:P1082 ?population.  # Population
  ?country wdt:P30 wd:Q15.      # Filtre : Afrique
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
ORDER BY DESC(?population)
LIMIT 150
"""

ROADS_QUERY = """
SELECT ?roadLabel ?countryLabel ?length WHERE {
  ?road wdt:P31 wd:Q34442;  # routes et autoroutes
        wdt:P17 ?country;  # pays
        wdt:P2043 ?length.  # longueur
  ?country wdt:P30 wd:Q15.  # filtre: afrique
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
ORDER BY DESC(?length)
LIMIT 100
"""

EVOLUTION_QUERY = """
SELECT ?cityLabel ?year ?population WHERE {
  ?city wdt:P31 wd:Q515;  # ville
        wdt:P17 ?country;  # pays
        p:P1082 ?popStatement.  # population avec historique
  ?popStatement ps:P1082 ?population; pq:P585 ?year.  # associer année et population
  ?country wdt:P30 wd:Q15.  # afrique
  FILTER(YEAR(?year) >= 1970)  # filtrer les données après 1970
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
ORDER BY ?city ?year
"""

@st.cache_data(ttl=3600)
def load_live_cities():
    extractor = WikidataExtractor()
    df = extractor.fetch_data(CITIES_QUERY)
    if not df.empty:
        df["population"] = pd.to_numeric(df["population"], errors='coerce')
    return df

@st.cache_data(ttl=3600)
def load_live_roads():
    extractor = WikidataExtractor()
    df = extractor.fetch_data(ROADS_QUERY)
    if not df.empty:
        df["length"] = pd.to_numeric(df["length"], errors='coerce')
    return df

@st.cache_data(ttl=3600)
def load_live_evolution():
    extractor = WikidataExtractor()
    df = extractor.fetch_data(EVOLUTION_QUERY)
    if not df.empty:
        df["population"] = pd.to_numeric(df["population"], errors='coerce')
        df["year"] = pd.to_datetime(df["year"], errors='coerce').dt.year
        df = df.dropna(subset=["year", "population"])
        df["year"] = df["year"].astype(int)
    return df

with st.spinner("Connexion à Wikidata et synchronisation en temps réel de tous les jeux de données..."):
    df_cities = load_live_cities()
    df_roads = load_live_roads()
    df_urban = load_live_evolution()
if df_cities.empty or df_roads.empty or df_urban.empty:
    st.error("Impossible de récupérer les données en direct depuis Wikidata. Veuillez vérifier votre connexion.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Grandes Villes (Live)", "Infrastructures Routières (Live)", "Évolution Urbaine (Live)"])

with tab1:
    st.subheader("Les plus grandes villes africaines (Données Wikidata en direct)")
    top_n = st.slider("Nombre de villes à afficher", 5, 50, 10)
    
    fig_cities = px.bar(
        df_cities.head(top_n), 
        x="population", 
        y="cityLabel", 
        orientation='h',
        color="population",
        labels={"cityLabel": "Villes", "population": "Population"},
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig_cities.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cities, use_container_width=True)

with tab2:
    st.subheader("Infrastructures Routières (Données Wikidata en direct)")
    df_roads_unique = df_roads.drop_duplicates(subset=["roadLabel", "length"])
    top_roads_n = st.slider("Nombre de routes à afficher", 5, 30, 10)
    
    fig_roads = px.bar(
        df_roads_unique.head(top_roads_n), 
        x="length", 
        y="roadLabel", 
        orientation='h',
        color="length",
        labels={"roadLabel": "Routes", "length": "Longueur (km)"},
        color_continuous_scale=px.colors.sequential.Oranges
    )
    fig_roads.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_roads, use_container_width=True)

with tab3:
    st.subheader("Évolution de la population urbaine (Données Wikidata en direct)")
    cities_list = sorted(df_urban["cityLabel"].unique())
    
    candidates = ["Alexandrie", "Alexandria", "Casablanca", "Lagos", "Abidjan"]
    
    default_selections = [c for c in candidates if c in cities_list]
    
    if not default_selections and len(cities_list) >= 3:
        default_selections = cities_list[:3]
    
    selected_cities = st.multiselect(
        "Sélectionner des villes", 
        cities_list, 
        default=default_selections
    )
    
    if selected_cities:
        df_filtered = df_urban[df_urban["cityLabel"].isin(selected_cities)]
        
        fig_line = px.line(
            df_filtered, 
            x="year", 
            y="population", 
            color="cityLabel",
            markers=True,
            labels={"year": "Année", "population": "Population"}
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Veuillez sélectionner au moins une ville pour visualiser son évolution historique.")