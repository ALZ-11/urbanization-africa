import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Urbanisation en Afrique")

st.title("Big Data et Urbanisation en Afrique")
st.markdown("""
Analyse exploratoire des dynamiques urbaines et infrastructures routières africaines. 
Données extraites de **Wikidata** via des requêtes **SPARQL**.
""")

DATA_DIR = "data"

@st.cache_data
def load_data():
    df_cities = pd.read_csv(os.path.join(DATA_DIR, "biggest_cities.csv"))
    df_roads = pd.read_csv(os.path.join(DATA_DIR, "longest_roads.csv"))
    df_urban = pd.read_csv(os.path.join(DATA_DIR, "urban_evolution.csv"))
    return df_cities, df_roads, df_urban

try:
    df_cities, df_roads, df_urban = load_data()
except Exception as e:
    st.error(f"Erreur de chargement des fichiers : {e}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Grandes Villes", "Infrastructures Routières", "Évolution Urbaine"])

with tab1:
    st.subheader("Les plus grandes villes africaines")
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
    st.subheader("Infrastructures Routières (Routes et Autoroutes)")
    df_roads_unique = df_roads.drop_duplicates(subset=["roadLabel", "length"])
    df_roads_unique["length"] = pd.to_numeric(df_roads_unique["length"], errors='coerce')
    
    fig_roads = px.bar(
        df_roads_unique.head(10), 
        x="length", 
        y="roadLabel", 
        orientation='h',
        labels={"roadLabel": "Routes", "length": "Longueur (km)"},
        color_discrete_sequence=["orange"]
    )
    fig_roads.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_roads, use_container_width=True)

with tab3:
    st.subheader("Évolution de la population urbaine (Multiville)")
    cities_list = sorted(df_urban["cityLabel"].unique())
    selected_cities = st.multiselect("Sélectionner des villes", cities_list, default=["Alexandria", "Casablanca", "Lagos"])
    
    if selected_cities:
        df_filtered = df_urban[df_urban["cityLabel"].isin(selected_cities)]
        df_filtered["year"] = pd.to_datetime(df_filtered["year"]).dt.year
        
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
        st.info("Veuillez sélectionner au moins une ville.")