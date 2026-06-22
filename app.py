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
SELECT ?cityLabel ?countryLabel ?population ?coords WHERE {
  ?city wdt:P31 wd:Q515;        # Ville
        wdt:P17 ?country;       # Pays
        wdt:P1082 ?population;  # Population
        wdt:P625 ?coords.       # Coordonnées géographiques
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

AIRPORTS_QUERY = """
SELECT ?airportLabel ?countryLabel ?iata ?coords ?elevation WHERE {
  ?airport wdt:P31 wd:Q1248784; # Aéroport
           wdt:P17 ?country;
           wdt:P625 ?coords.
  ?country wdt:P30 wd:Q15.     # Afrique
  OPTIONAL { ?airport wdt:P238 ?iata. } # Code IATA
  OPTIONAL { ?airport wdt:P2044 ?elevation. } # Altitude (mètres)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
ORDER BY DESC(?elevation)
LIMIT 150
"""

@st.cache_data(ttl=3600)
def load_live_cities():
    extractor = WikidataExtractor()
    df = extractor.fetch_data(CITIES_QUERY)
    if not df.empty:
        df["population"] = pd.to_numeric(df["population"], errors='coerce')
        df['latitude'] = None
        df['longitude'] = None
        for idx, row in df.iterrows():
            coords_str = row.get('coords')
            if isinstance(coords_str, str) and coords_str.startswith("Point("):
                try:
                    lon_lat_str = coords_str.replace("Point(", "").replace(")", "").split(" ")
                    df.at[idx, 'longitude'] = float(lon_lat_str[0])
                    df.at[idx, 'latitude'] = float(lon_lat_str[1])
                except (ValueError, IndexError):
                    pass
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
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

@st.cache_data(ttl=3600)
def load_live_airports():
    extractor = WikidataExtractor()
    df = extractor.fetch_data(AIRPORTS_QUERY)
    if not df.empty:
        df["elevation"] = pd.to_numeric(df["elevation"], errors='coerce')
        df['latitude'] = None
        df['longitude'] = None
        for idx, row in df.iterrows():
            coords_str = row.get('coords')
            if isinstance(coords_str, str) and coords_str.startswith("Point("):
                try:
                    lon_lat_str = coords_str.replace("Point(", "").replace(")", "").split(" ")
                    df.at[idx, 'longitude'] = float(lon_lat_str[0])
                    df.at[idx, 'latitude'] = float(lon_lat_str[1])
                except (ValueError, IndexError):
                    pass
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    return df

with st.spinner("Connexion à Wikidata et synchronisation globale de l'ensemble des réseaux d'infrastructures..."):
    df_cities = load_live_cities()
    df_roads = load_live_roads()
    df_urban = load_live_evolution()
    df_airports = load_live_airports()

if df_cities.empty or df_roads.empty or df_urban.empty or df_airports.empty:
    st.error("Impossible de récupérer l'ensemble des données depuis Wikidata. Veuillez vérifier votre connexion.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "Cartographie & Démographie", 
    "Infrastructures Routières", 
    "Évolution Urbaine",
    "Réseau Aéroportuaire"
])

with tab1:
    st.subheader("Distribution et Démographie des Villes Africaines")
    df_map = df_cities.dropna(subset=["latitude", "longitude"])
    if not df_map.empty:
        fig_map = px.scatter_mapbox(
            df_map,
            lat="latitude",
            lon="longitude",
            size="population",
            color="population",
            hover_name="cityLabel",
            hover_data={"countryLabel": True, "population": True, "latitude": False, "longitude": False},
            color_continuous_scale=px.colors.sequential.Blues,
            size_max=35,
            zoom=2.5,
            height=500,
            mapbox_style="open-street-map"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Aucune coordonnée valide trouvée pour la cartographie.")

    st.markdown("---")
    top_n = st.slider("Nombre de villes à afficher dans le classement", 5, 50, 10)
    
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

with tab4:
    st.subheader("Réseau des Plateformes Aéroportuaires en Afrique")
    
    df_airports_map = df_airports.dropna(subset=["latitude", "longitude"])
    if not df_airports_map.empty:
        fig_airports_map = px.scatter_mapbox(
            df_airports_map,
            lat="latitude",
            lon="longitude",
            hover_name="airportLabel",
            hover_data={"countryLabel": True, "iata": True, "elevation": True, "latitude": False, "longitude": False},
            color_discrete_sequence=["teal"],
            zoom=2.5,
            height=500,
            mapbox_style="open-street-map"
        )
        fig_airports_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_airports_map, use_container_width=True)
    else:
        st.warning("Aucune coordonnée valide trouvée pour cartographier les aéroports.")
        
    st.markdown("---")
    
    st.subheader("Aéroports les plus élevés d'Afrique (Altitude au-dessus du niveau de la mer)")
    df_elevation = df_airports.dropna(subset=["elevation"])
    top_elevated_n = st.slider("Nombre d'aéroports à afficher", 5, 30, 10, key="elev_slider")
    
    fig_elevation = px.bar(
        df_elevation.head(top_elevated_n),
        x="elevation",
        y="airportLabel",
        orientation="h",
        color="elevation",
        labels={"airportLabel": "Aéroports", "elevation": "Altitude (mètres)"},
        color_continuous_scale=px.colors.sequential.Tealgrn
    )
    fig_elevation.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_elevation, use_container_width=True)