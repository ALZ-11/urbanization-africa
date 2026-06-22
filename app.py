import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import numpy as np
from src.queries import get_query
import src.extract as extract
import src.transform as transform

st.set_page_config(layout="wide", page_title="Urbanisation en Afrique")

st.title("Big Data et Urbanisation en Afrique")
st.markdown("""
Analyse exploratoire des dynamiques urbaines et infrastructures routières africaines. 
Données extraites en temps réel de **Wikidata** via des requêtes **SPARQL**.
""")

CITIES_QUERY = get_query("cities")
ROADS_QUERY = get_query("roads")
EVOLUTION_QUERY = get_query("evolution")
AIRPORTS_QUERY = get_query("airports")
PORTS_QUERY = get_query("ports")

COUNTRY_ISO_MAP = {
    "Afrique du Sud": "ZA", "Algérie": "DZ", "Angola": "AO", "Bénin": "BJ", "Botswana": "BW",
    "Burkina Faso": "BF", "Burundi": "BI", "Cabo Verde": "CV", "Cameroun": "CM", "Centrafrique": "CF",
    "Comores": "KM", "Congo-Brazzaville": "CG", "Congo-Kinshasa": "CD", "Côte d'Ivoire": "CI",
    "Djibouti": "DJ", "Égypte": "EG", "Érythrée": "ER", "Eswatini": "SZ", "Éthiopie": "ET",
    "Gabon": "GA", "Gambie": "GM", "Ghana": "GH", "Guinée": "GN", "Guinée-Bissau": "GW",
    "Guinée équatoriale": "GQ", "Kenya": "KE", "Lesotho": "LS", "Liberia": "LR", "Libye": "LY",
    "Madagascar": "MG", "Malawi": "MW", "Mali": "ML", "Maroc": "MA", "Maurice": "MU",
    "Mauritanie": "MR", "Mozambique": "MZ", "Namibie": "NA", "Niger": "NE", "Nigéria": "NG",
    "Ouganda": "UG", "Rwanda": "RW", "Sao Tomé-et-Principe": "ST", "Sénégal": "SN", "Seychelles": "SC",
    "Sierra Leone": "SL", "Somalie": "SO", "Soudan": "SD", "Soudan du Sud": "SS", "Tanzanie": "TZ",
    "Tchad": "TD", "Togo": "TG", "Tunisie": "TN", "Zambie": "ZM", "Zimbabwe": "ZW"
}

@st.cache_data(ttl=3600)
def load_live_cities():
    extractor = extract.WikidataExtractor()
    df = extractor.fetch_data(CITIES_QUERY)
    return transform.transform_cities(df)

@st.cache_data(ttl=3600)
def load_live_roads():
    extractor = extract.WikidataExtractor()
    df = extractor.fetch_data(ROADS_QUERY)
    return transform.transform_roads(df)

@st.cache_data(ttl=3600)
def load_live_evolution():
    extractor = extract.WikidataExtractor()
    df = extractor.fetch_data(EVOLUTION_QUERY)
    return transform.transform_evolution(df)

@st.cache_data(ttl=3600)
def load_live_airports():
    extractor = extract.WikidataExtractor()
    df = extractor.fetch_data(AIRPORTS_QUERY)
    return transform.transform_airports(df)

@st.cache_data(ttl=3600)
def load_live_ports():
    extractor = extract.WikidataExtractor()
    df = extractor.fetch_data(PORTS_QUERY)
    return transform.transform_ports(df)

@st.cache_data(ttl=86400)
def load_world_bank_data(country_code):
    extractor = extract.WorldBankExtractor()
    raw_data = extractor.fetch_urban_data(country_code)
    return transform.transform_world_bank(raw_data)

@st.cache_data
def convert_to_downloadable_csv(df):
    return df.to_csv(index=False).encode("utf-8")

start_time = time.time()

with st.spinner("Connexion à Wikidata et synchronisation globale de l'ensemble des réseaux d'infrastructures..."):
    df_cities = load_live_cities()
    df_roads = load_live_roads()
    df_urban = load_live_evolution()
    df_airports = load_live_airports()
    df_ports = load_live_ports()

latency = time.time() - start_time

if df_cities.empty or df_roads.empty or df_urban.empty or df_airports.empty or df_ports.empty:
    st.error("Impossible de récupérer l'ensemble des données depuis Wikidata. Veuillez vérifier votre connexion.")
    st.stop()

st.sidebar.header("Exportation des Donnees")
st.sidebar.markdown("""
Telechargez les jeux de donnees compiles en temps reel depuis le triple-store de Wikidata.
""")

if not df_cities.empty:
    csv_cities = convert_to_downloadable_csv(df_cities[["cityLabel", "countryLabel", "population", "latitude", "longitude"]])
    st.sidebar.download_button(
        label="Telecharger Villes (CSV)",
        data=csv_cities,
        file_name="villes_afrique_live.csv",
        mime="text/csv"
    )

if not df_roads.empty:
    csv_roads = convert_to_downloadable_csv(df_roads.drop_duplicates(subset=["roadLabel", "length"]))
    st.sidebar.download_button(
        label="Telecharger Routes (CSV)",
        data=csv_roads,
        file_name="routes_afrique_live.csv",
        mime="text/csv"
    )

if not df_airports.empty:
    csv_airports = convert_to_downloadable_csv(df_airports[["airportLabel", "countryLabel", "iata", "elevation", "latitude", "longitude"]])
    st.sidebar.download_button(
        label="Telecharger Aeroports (CSV)",
        data=csv_airports,
        file_name="aeroports_afrique_live.csv",
        mime="text/csv"
    )

if not df_ports.empty:
    csv_ports = convert_to_downloadable_csv(df_ports[["portLabel", "countryLabel", "latitude", "longitude"]])
    st.sidebar.download_button(
        label="Telecharger Ports (CSV)",
        data=csv_ports,
        file_name="ports_afrique_live.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.subheader("Performances du Pipeline")
st.sidebar.metric(
    label="Latence du Pipeline (Wikidata)",
    value=f"{latency:.2f}s",
    delta="Via Cache" if latency < 0.1 else "Extraction Live (Reseau)",
    delta_color="normal" if latency < 0.1 else "inverse"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Cartographie & Démographie", 
    "Infrastructures Routières", 
    "Évolution Urbaine",
    "Réseaux Logistiques",
    "Analyses par Pays"
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
    
    st.markdown("---")
    st.subheader("Densite du Reseau de Transit: Nombre de Couloirs Routiers Majeurs par Pays")
    
    df_transit_density = df_roads.groupby("countryLabel")["roadLabel"].nunique().reset_index()
    df_transit_density = df_transit_density.rename(
        columns={"countryLabel": "Pays", "roadLabel": "Nombre de couloirs"}
    ).sort_values("Nombre de couloirs", ascending=False).head(15)
    
    fig_transit = px.bar(
        df_transit_density,
        x="Pays",
        y="Nombre de couloirs",
        color="Nombre de couloirs",
        color_continuous_scale=px.colors.sequential.Oranges,
        labels={"Pays": "Pays", "Nombre de couloirs": "Nombre de Couloirs"}
    )
    st.plotly_chart(fig_transit, use_container_width=True)

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
        
        display_metrics = selected_cities[:4]
        cols = st.columns(len(display_metrics))
        
        for idx, city in enumerate(display_metrics):
            df_city_only = df_filtered[df_filtered["cityLabel"] == city].sort_values("year")
            if len(df_city_only) >= 2:
                first_rec = df_city_only.iloc[0]
                last_rec = df_city_only.iloc[-1]
                
                growth_rate = ((last_rec["population"] - first_rec["population"]) / first_rec["population"]) * 100
                timespan = last_rec["year"] - first_rec["year"]
                
                with cols[idx]:
                    st.metric(
                        label=f"{city} ({int(first_rec['year'])} - {int(last_rec['year'])})",
                        value=f"{int(last_rec['population']):,}",
                        delta=f"+{growth_rate:.1f}% sur {int(timespan)} ans"
                    )
                    
        st.markdown("---")
        
        show_projections = st.checkbox("Afficher les projections lineaires de croissance demographique (jusqu'en 2035)", value=False)
        
        df_filtered["Statut"] = "Historique"
        df_combined_plot = df_filtered.copy()
        
        if show_projections:
            projection_records = []
            for city in selected_cities:
                df_city = df_filtered[df_filtered["cityLabel"] == city].sort_values("year")
                if len(df_city) >= 2:
                    x_years = df_city["year"].values
                    y_pops = df_city["population"].values
                    
                    slope, intercept = np.polyfit(x_years, y_pops, 1)
                    
                    last_year = int(x_years[-1])
                    
                    if last_year < 2035:
                        projection_records.append({
                            "cityLabel": city,
                            "year": last_year,
                            "population": int(y_pops[-1]),
                            "Statut": "Projection"
                        })
                        
                        forecast_years = list(range(last_year + 5, 2036, 5))
                        if 2035 not in forecast_years:
                            forecast_years.append(2035)
                            
                        for f_year in forecast_years:
                            predicted_pop = slope * f_year + intercept
                            projection_records.append({
                                "cityLabel": city,
                                "year": f_year,
                                "population": max(0, int(predicted_pop)),
                                "Statut": "Projection"
                            })
                            
            if projection_records:
                df_proj = pd.DataFrame(projection_records)
                df_combined_plot = pd.concat([df_filtered, df_proj], ignore_index=True)
        
        fig_line = px.line(
            df_combined_plot, 
            x="year", 
            y="population", 
            color="cityLabel",
            line_dash="Statut",
            markers=True,
            labels={"year": "Année", "population": "Population", "Statut": "Statut de la donnee"}
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Veuillez sélectionner au moins une ville pour visualiser son évolution historique.")

with tab4:
    st.subheader("Réseaux d'Échanges Maritimes et Aériens")
    
    logistic_features = []
    
    for _, row in df_airports.dropna(subset=["latitude", "longitude"]).iterrows():
        logistic_features.append({
            "Nom": row["airportLabel"],
            "Latitude": row["latitude"],
            "Longitude": row["longitude"],
            "Type": "Aeroport",
            "Details": f"Code IATA: {row['iata']}" if isinstance(row['iata'], str) else "Code IATA: N/A"
        })
        
    for _, row in df_ports.dropna(subset=["latitude", "longitude"]).iterrows():
        logistic_features.append({
            "Nom": row["portLabel"],
            "Latitude": row["latitude"],
            "Longitude": row["longitude"],
            "Type": "Port Maritime",
            "Details": f"Pays: {row['countryLabel']}"
        })
        
    if logistic_features:
        df_logistics = pd.DataFrame(logistic_features)
        fig_logistics = px.scatter_mapbox(
            df_logistics,
            lat="Latitude",
            lon="Longitude",
            color="Type",
            hover_name="Nom",
            hover_data={"Type": True, "Details": True, "Latitude": False, "Longitude": False},
            color_discrete_map={"Aeroport": "teal", "Port Maritime": "darkblue"},
            zoom=2.5,
            height=500,
            mapbox_style="open-street-map"
        )
        fig_logistics.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_logistics, use_container_width=True)
    else:
        st.warning("Aucune coordonnée valide trouvée pour cartographier les infrastructures.")
        
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

with tab5:
    st.subheader("Profils de Developpement et Taux d'Urbanisation Nationale")
    st.markdown("""
    Cette section croise les données de Wikidata avec les indicateurs macroéconomiques de la **Banque Mondiale** 
    pour suivre le taux d'urbanisation (pourcentage de la population totale vivant en milieu urbain).
    """)
    
    selectable_countries = sorted(list(COUNTRY_ISO_MAP.keys()))
    selected_country = st.selectbox("Choisir un pays pour l'analyse nationale", selectable_countries)
    
    if selected_country:
        iso_code = COUNTRY_ISO_MAP[selected_country]
        
        with st.spinner(f"Chargement des indicateurs de la Banque Mondiale pour le pays: {selected_country}..."):
            df_wb = load_world_bank_data(iso_code)
            
        if not df_wb.empty:
            fig_wb = px.line(
                df_wb,
                x="year",
                y="urban_rate",
                markers=True,
                labels={"year": "Annee", "urban_rate": "Taux d'urbanisation (en %)"},
                color_discrete_sequence=["purple"]
            )
            fig_wb.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_wb, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                initial_rate = df_wb.iloc[0]["urban_rate"]
                initial_year = df_wb.iloc[0]["year"]
                st.metric(label=f"Taux d'urbanisation initial ({initial_year})", value=f"{initial_rate:.1f}%")
            with col2:
                latest_rate = df_wb.iloc[-1]["urban_rate"]
                latest_year = df_wb.iloc[-1]["year"]
                st.metric(label=f"Taux d'urbanisation le plus recent ({latest_year})", value=f"{latest_rate:.1f}%")
                
            df_country_cities = df_cities[df_cities["countryLabel"] == selected_country]
            df_country_airports = df_airports[df_airports["countryLabel"] == selected_country]
            df_country_ports = df_ports[df_ports["countryLabel"] == selected_country]
            
            local_features = []
            
            if not df_country_cities.empty:
                for _, row in df_country_cities.dropna(subset=["latitude", "longitude"]).iterrows():
                    local_features.append({
                        "Nom": row["cityLabel"],
                        "Latitude": row["latitude"],
                        "Longitude": row["longitude"],
                        "Type": "Ville",
                        "Taille": row["population"] / 200000 + 5
                    })
                    
            if not df_country_airports.empty:
                for _, row in df_country_airports.dropna(subset=["latitude", "longitude"]).iterrows():
                    local_features.append({
                        "Nom": row["airportLabel"],
                        "Latitude": row["latitude"],
                        "Longitude": row["longitude"],
                        "Type": "Aeroport",
                        "Taille": 8
                    })
            
            if not df_country_ports.empty:
                for _, row in df_country_ports.dropna(subset=["latitude", "longitude"]).iterrows():
                    local_features.append({
                        "Nom": row["portLabel"],
                        "Latitude": row["latitude"],
                        "Longitude": row["longitude"],
                        "Type": "Port Maritime",
                        "Taille": 8
                    })
            
            if local_features:
                st.markdown("---")
                st.subheader(f"Repartion des Infrastructures Démographiques et Aéroportuaires : {selected_country}")
                
                df_local_map = pd.DataFrame(local_features)
                fig_local = px.scatter_mapbox(
                    df_local_map,
                    lat="Latitude",
                    lon="Longitude",
                    color="Type",
                    size="Taille",
                    hover_name="Nom",
                    hover_data={"Type": True, "Taille": False, "Latitude": False, "Longitude": False},
                    color_discrete_map={"Ville": "blue", "Aeroport": "teal", "Port Maritime": "darkblue"},
                    zoom=4.5,
                    height=500,
                    mapbox_style="open-street-map"
                )
                fig_local.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig_local, use_container_width=True)
                
            df_country_roads = df_roads[df_roads["countryLabel"] == selected_country]
            
            if not df_country_roads.empty:
                st.markdown("---")
                st.subheader(f"Principales Infrastructures Routieres Traversantes : {selected_country}")
                
                df_roads_display = df_country_roads.drop_duplicates(subset=["roadLabel", "length"])
                df_roads_display = df_roads_display[["roadLabel", "length"]].rename(
                    columns={"roadLabel": "Nom de la Route / Autoroute", "length": "Longueur Totale de la Route (km)"}
                )
                
                st.dataframe(df_roads_display, use_container_width=True, hide_index=True)
                
        else:
            st.warning("Aucune donnee trouvee pour ce pays auprès de la Banque Mondiale.")