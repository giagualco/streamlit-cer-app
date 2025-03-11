import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim

# ---- Caricamento credenziali Google ----
try:
    credentials_info = json.loads(st.secrets["google_credentials"])
    credentials = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(credentials)
    st.success("✅ Autenticazione con Google riuscita!")
except Exception as e:
    st.error(f"Errore di autenticazione con Google: {e}")
    st.stop()

# ---- Connessione al foglio Google Sheets ----
SHEET_NAME = "Dati_Condomini"
try:
    sheet = gc.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()
    st.success("✅ Connessione al Google Sheet riuscita!")
except Exception as e:
    st.error(f"Errore nell'aprire il foglio: {e}")
    st.stop()

# ---- Interfaccia Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# Sezione dati condomini
st.subheader("📋 Dati dei Condomini")
df = sheet.get_all_records()
st.dataframe(df)

# Sezione mappa interattiva
st.subheader("📍 Mappa dei Condomini")

def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app")
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude] if location else None
    except:
        return None

# Creazione mappa con Esri Satellite
m = folium.Map(location=[45.0703, 7.6869], zoom_start=15, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr='Esri')

# Aggiunta strumenti di ricerca e misurazione
from folium.plugins import LocateControl, MeasureControl, Search
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)
search = Search(layer=m, geom_type='Point', placeholder='Cerca un indirizzo', collapsed=False).add_to(m)

# Aggiunta punti per i condomini
data = sheet.get_all_records()
for row in data:
    address = row.get("Indirizzo", "")
    coords = get_coordinates(address)
    if coords:
        folium.Marker(
            location=coords,
            popup=f"{row['Nome Condominio']}\n{address}",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)

st_folium(m, width=800, height=500)
