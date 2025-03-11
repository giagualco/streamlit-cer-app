import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl, Search

# Definisci gli scopes necessari
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",  # Accesso a Google Sheets
    "https://www.googleapis.com/auth/drive",         # Accesso a Google Drive (opzionale)
]

# ---- Funzione per caricare le credenziali Google ----
def load_google_credentials():
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        st.success("✅ Autenticazione con Google riuscita!")
        return gc
    except Exception as e:
        st.error(f"Errore di autenticazione con Google: {e}")
        st.stop()

# ---- Funzione per ottenere i dati dal foglio Google Sheets ----
@st.cache_data  # Memorizza solo i dati (hashabili)
def get_sheet_data(sheet_name):
    try:
        gc = load_google_credentials()  # Creiamo una nuova connessione qui
        sheet = gc.open(sheet_name).sheet1
        data = sheet.get_all_records()
        st.success("✅ Connessione al Google Sheet riuscita!")
        return data
    except Exception as e:
        st.error(f"Errore nell'aprire il foglio: {e}")
        st.stop()

# ---- Funzione per ottenere le coordinate di un indirizzo ----
@st.cache_data  # Memorizza le coordinate per evitare chiamate ripetute
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

# Caricamento dati dal foglio Google Sheets
SHEET_NAME = "Dati_Condomini"
data = get_sheet_data(SHEET_NAME)  # Ottieni i dati memorizzati nella cache

# Sezione dati condomini
st.subheader("📋 Dati dei Condomini")
st.dataframe(data)  # Utilizzo dei dati già caricati

# Sezione mappa interattiva
st.subheader("📍 Mappa dei Condomini")

# Creazione mappa con Esri Satellite
m = folium.Map(location=[45.0703, 7.6869], zoom_start=15, 
               tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", 
               attr='Esri')

# Creazione di un FeatureGroup per i marker dei condomini
condominio_layer = folium.FeatureGroup(name="Condomini")

# Aggiunta punti per i condomini al FeatureGroup
for row in data:
    address = row.get("Indirizzo", "")
    coords = get_coordinates(address)
    if coords:
        folium.Marker(
            location=coords,
            popup=f"{row['Nome Condominio']}\n{address}",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(condominio_layer)  # Aggiungi il marker al FeatureGroup

# Aggiunta del FeatureGroup alla mappa
condominio_layer.add_to(m)

# Aggiunta strumenti di ricerca e misurazione
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)

# Configurazione del plugin Search per cercare nei marker del FeatureGroup
search = Search(
    layer=condominio_layer,  # Passa il FeatureGroup come layer
    geom_type='Point',
    placeholder='Cerca un indirizzo',
    collapsed=False
).add_to(m)

# Visualizzazione della mappa
st_folium(m, width=800, height=500)
