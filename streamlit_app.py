import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl, Search

# ---- Funzione per caricare le credenziali Google ----
@st.cache_data
def load_google_credentials():
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info)
        gc = gspread.authorize(credentials)
        st.success("✅ Autenticazione con Google riuscita!")
        return gc
    except Exception as e:
        st.error(f"Errore di autenticazione con Google: {e}")
        st.stop()

# ---- Funzione per connettersi al foglio Google Sheets ----
@st.cache_data
def connect_to_google_sheet(gc, sheet_name):
    try:
        sheet = gc.open(sheet_name).sheet1
        data = sheet.get_all_records()
        st.success("✅ Connessione al Google Sheet riuscita!")
        return sheet, data
    except Exception as e:
        st.error(f"Errore nell'aprire il foglio: {e}")
        st.stop()

# ---- Funzione per ottenere le coordinate di un indirizzo ----
@st.cache_data
def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app", timeout=10)  # Aggiunto timeout
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude] if location else None
    except Exception as e:
        st.warning(f"Errore durante la geolocalizzazione di {address}: {e}")
        return None

# ---- Interfaccia Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Caricamento credenziali e connessione al foglio
gc = load_google_credentials()
SHEET_NAME = "Dati_Condomini"
sheet, data = connect_to_google_sheet(gc, SHEET_NAME)

# Sezione dati condomini
st.subheader("📋 Dati dei Condomini")
st.dataframe(data)  # Utilizzo dei dati già caricati

# Sezione mappa interattiva
st.subheader("📍 Mappa dei Condomini")

# Creazione mappa con Esri Satellite
m = folium.Map(location=[45.0703, 7.6869], zoom_start=15, 
               tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", 
               attr='Esri')

# Aggiunta strumenti di ricerca e misurazione
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)
search = Search(layer=m, geom_type='Point', placeholder='Cerca un indirizzo', collapsed=False).add_to(m)

# Aggiunta punti per i condomini
for row in data:
    address = row.get("Indirizzo", "")
    coords = get_coordinates(address)
    if coords:
        folium.Marker(
            location=coords,
            popup=f"{row['Nome Condominio']}\n{address}",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)

# Visualizzazione della mappa
st_folium(m, width=800, height=500)
