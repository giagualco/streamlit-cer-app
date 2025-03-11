import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl, Search

# ---- Definizione degli scope Google ----
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---- Funzione per caricare le credenziali Google ----
def load_google_credentials():
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"❌ Errore di autenticazione con Google: {e}")
        st.stop()

# ---- Funzione per ottenere i dati dal foglio Google Sheets ----
@st.cache_data
def get_sheet_data(sheet_name):
    try:
        gc = load_google_credentials()
        sheet = gc.open(sheet_name).sheet1
        return sheet.get_all_records()
    except Exception as e:
        st.error(f"❌ Errore nell'aprire il foglio: {e}")
        return []

# ---- Funzione per ottenere le coordinate di un indirizzo ----
@st.cache_data
def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app", timeout=10)
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude] if location else None
    except Exception as e:
        st.warning(f"⚠️ Errore durante la geolocalizzazione di {address}: {e}")
        return None

# ---- Interfaccia Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Caricamento dati dal foglio Google Sheets
SHEET_NAME = "Dati_Condomini"
data = get_sheet_data(SHEET_NAME)

# Sezione dati condomini
st.subheader("📋 Dati dei Condomini")
if data:
    st.dataframe(data)
else:
    st.warning("⚠️ Nessun dato disponibile nel foglio Google Sheets.")

# Sezione mappa interattiva
st.subheader("📍 Mappa dei Condomini")

# Creazione mappa con sfondo satellitare Google
m = folium.Map(
    location=[45.0703, 7.6869], 
    zoom_start=17,
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google Maps"
)

# Creazione di un FeatureGroup per i marker
condominio_layer = folium.FeatureGroup(name="Condomini")

# Aggiunta punti per i condomini
for row in data:
    address = row.get("Indirizzo", "")
    coords = get_coordinates(address)
    if coords:
        folium.Marker(
            location=coords,
            popup=f"{row['Nome Condominio']}\n{address}",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(condominio_layer)

# Aggiunta FeatureGroup alla mappa
condominio_layer.add_to(m)

# Aggiunta strumenti di localizzazione, misurazione e ricerca
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)
search = Search(
    layer=condominio_layer,
    search_label="Nome Condominio",
    geom_type='Point',
    placeholder='🔍 Cerca un condominio',
    collapsed=False
).add_to(m)

# Visualizzazione della mappa
st_folium(m, width=1000, height=600)
