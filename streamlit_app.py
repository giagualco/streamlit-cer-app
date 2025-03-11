import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, MeasureControl
from google.oauth2.service_account import Credentials
import gspread

# ---- CONFIGURAZIONE GOOGLE SHEETS ----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["google_credentials"], scopes=scope)

# Connessione a Google Sheets
gc = gspread.authorize(credentials)
sheet = gc.open("Dati_Condomini").sheet1  # Assicurati che il foglio esista

# Carica i dati in un DataFrame
data = pd.DataFrame(sheet.get_all_records())

# ---- INTERFACCIA STREAMLIT ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Mostra i dati in una tabella
st.subheader("📋 Dati dei Condomini")
st.dataframe(data)

# ---- MAPPA CONDOMINI ----
st.subheader("📍 Mappa dei Condomini")

# Configura la mappa Folium con sfondo satellitare
m = folium.Map(
    location=[45.0703, 7.6869],  # Centro su Torino (modificabile)
    zoom_start=15,
    tiles="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri, Maxar, Earthstar Geographics"
)

# Aggiunge il pulsante di localizzazione
LocateControl(auto_start=False).add_to(m)

# Aggiunge lo strumento di misura
MeasureControl(primary_length_unit='meters').add_to(m)

# Aggiunge i marker sulla mappa
for _, row in data.iterrows():
    if row["Indirizzo"]:
        folium.Marker(
            location=[row["Latitudine"], row["Longitudine"]],
            popup=f"{row['Nome Condominio']} - {row['Indirizzo']}",
            tooltip=row["Nome Condominio"],
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)

# Mostra la mappa in Streamlit
st_folium(m, width=700, height=500)
