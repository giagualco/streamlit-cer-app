import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl, Search

# Definiamo gli SCOPI per l'autenticazione Google
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ---- Funzione per caricare le credenziali Google ----
def load_google_credentials():
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        st.error("Errore di autenticazione con Google. Verifica le credenziali.")
        st.stop()

# ---- Funzione per ottenere i dati dal Google Sheet ----
@st.cache_data
def get_sheet_data(sheet_name):
    try:
        gc = load_google_credentials()
        sheet = gc.open(sheet_name).sheet1
        data = sheet.get_all_records()
        return data
    except Exception:
        return []  # Se c'è un errore, restituisci una lista vuota senza interrompere

# ---- Funzione per ottenere le coordinate da un indirizzo ----
@st.cache_data
def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app", timeout=10)
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude] if location else None
    except:
        return None

# ---- Interfaccia Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Caricamento dati dal foglio Google Sheets
SHEET_NAME = "Dati_Condomini"
data = get_sheet_data(SHEET_NAME)

# Controllo se ci sono dati
if not data:
    st.warning("⚠️ Nessun dato disponibile al momento. Controlla il foglio Google Sheets.")
else:
    # ---- SEZIONE MAPPA INTERATTIVA ----
    st.subheader("📍 Mappa dei Condomini")

    # Mappa con sfondo satellitare ESRI
    m = folium.Map(location=[45.0703, 7.6869], zoom_start=15, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")

    # FeatureGroup per i marker dei condomini
    condominio_layer = folium.FeatureGroup(name="Condomini")

    # Aggiunta punti sulla mappa
    for row in data:
        address = row.get("Indirizzo", "")
        coords = get_coordinates(address)
        if coords:
            folium.Marker(
                location=coords,
                popup=f"{row['Nome Condominio']}\n{address}",
                icon=folium.Icon(color="blue", icon="home")
            ).add_to(condominio_layer)

    # Aggiungere strumenti utili
    condominio_layer.add_to(m)
    LocateControl(auto_start=False).add_to(m)  # Localizzazione
    MeasureControl(primary_length_unit='meters').add_to(m)  # Strumento di misurazione

    # Barra di ricerca
    search = Search(
        layer=condominio_layer,
        search_label="Nome Condominio",
        placeholder="Cerca un condominio",
        collapsed=False
    ).add_to(m)

    # Visualizzazione della mappa
    st_folium(m, width=850, height=550)
