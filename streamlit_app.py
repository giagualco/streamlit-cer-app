import streamlit as st
import pandas as pd
import folium
from folium.plugins import LocateControl, Draw
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# Titolo dell'app
st.title("Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Caricamento dati da Google Sheets (se disponibile)
st.subheader("📋 Dati dei Condomini")

# Simulazione di dati per la mappa (in attesa di connessione a Google Sheets)
data = pd.DataFrame({
    "Nome Condominio": ["Condominio A", "Condominio B"],
    "Indirizzo": ["Via Roma, Torino", "Corso Francia, Torino"],
    "Latitudine": [45.0703, 45.0805],
    "Longitudine": [7.6869, 7.6768]
})

st.write(data)

# Inizializzazione della mappa con sfondo satellitare
st.subheader("📍 Mappa dei Condomini")
m = folium.Map(location=[45.0703, 7.6869], zoom_start=15, tiles="Esri Satellite")

# Aggiunta dei marker dei condomini
for _, row in data.iterrows():
    folium.Marker(
        location=[row["Latitudine"], row["Longitudine"]],
        popup=row["Nome Condominio"],
        tooltip=row["Nome Condominio"]
    ).add_to(m)

# Aggiunta di strumenti di ricerca e misura
LocateControl().add_to(m)
Draw(export=True).add_to(m)

# Barra di ricerca per trovare gli indirizzi
geolocator = Nominatim(user_agent="streamlit_app")
address = st.text_input("🔍 Cerca un indirizzo sulla mappa", "")
if st.button("Cerca"):
    location = geolocator.geocode(address)
    if location:
        st.success(f"Trovato: {location.address}")
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup="Posizione Cercata",
            icon=folium.Icon(color="blue")
        ).add_to(m)
    else:
        st.error("Indirizzo non trovato. Riprova con un altro formato.")

# Visualizzazione della mappa
st_folium(m, width=800, height=600)
