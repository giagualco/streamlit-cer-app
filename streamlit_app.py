import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl

# ---- Configurazione Google Sheets ----
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Dati_Condomini"

# ---- Caricamento credenziali Google ----
def load_google_credentials():
    credentials_info = json.loads(st.secrets["google_credentials"])
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return gspread.authorize(credentials)

# ---- Funzione per salvare i dati nel Google Sheet ----
def save_data_to_sheet(data):
    try:
        gc = load_google_credentials()
        sheet = gc.open(SHEET_NAME).sheet1
        sheet.append_row(data)
        st.success("✅ Dati inviati con successo!")
    except Exception as e:
        st.error(f"❌ Errore nell'invio dei dati: {e}")

# ---- Funzione per ottenere le coordinate di un indirizzo ----
@st.cache_data
def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app")
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude] if location else None
    except:
        return None

# ---- UI Streamlit ----
st.title("📍 Rilevamento Condomini - Comunità Energetiche Rinnovabili (CER)")
st.write("Individua il condominio sulla mappa e trascina il PIN sul tetto.")

# ---- Sezione MAPPA ----
st.subheader("🔍 Cerca il condominio sulla mappa")
indirizzo = st.text_input("Inserisci l'indirizzo del condominio (usa Google Autocomplete)")
cerca = st.button("📍 Trova indirizzo")

# Creazione mappa con visualizzazione satellitare
m = folium.Map(location=[45.0703, 7.6869], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")

# Strumenti per ricerca e misurazione
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)

# Cerca indirizzo e piazza un marker trascinabile
if cerca and indirizzo:
    coords = get_coordinates(indirizzo)
    if coords:
        marker = folium.Marker(
            location=coords, 
            popup="Trascina il PIN sul tetto",
            draggable=True, 
            icon=folium.Icon(color="red")
        )
        marker.add_to(m)
        m.location = coords
    else:
        st.warning("⚠️ Indirizzo non trovato. Riprova con un altro.")

# Istruzioni per l’utente
st.markdown("➡️ **Istruzioni:** Cerca l'indirizzo, poi **trascina il PIN** per posizionarlo sul tetto corretto.")

# Mostra la mappa
map_data = st_folium(m, width=800, height=500)

# ---- Sezione MODULO RACCOLTA DATI ----
st.subheader("📋 Inserisci i dati del condominio")

nome_condominio = st.text_input("Nome del condominio")
riscaldamento = st.selectbox("Tipo di riscaldamento", ["Centralizzato", "Autonomo", "Nessuno"])
tipo_riscaldamento = st.selectbox("Tipologia", ["Gas", "Pompa di calore", "Ibrido"], disabled=(riscaldamento == "Nessuno"))
raffrescamento = st.selectbox("Raffrescamento centralizzato", ["Sì", "No"])
n_condomini = st.number_input("Numero di condomini", min_value=1, step=1)
stato_tetto = st.selectbox("Stato del tetto", ["Buono", "Mediocre", "Da rifare"])
n_appartamenti = st.number_input("Numero di appartamenti", min_value=1, step=1)
n_uffici = st.number_input("Numero di uffici", min_value=0, step=1)
n_negozi = st.number_input("Numero di negozi", min_value=0, step=1)

# ---- INVIA DATI ----
if st.button("📤 Invia dati"):
    if not nome_condominio or not indirizzo or not map_data["last_clicked"]:
        st.warning("⚠️ Devi inserire tutti i dati e trascinare il PIN sulla mappa!")
    else:
        lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        dati = [nome_condominio, indirizzo, lat, lon, riscaldamento, tipo_riscaldamento, raffrescamento, n_condomini, stato_tetto, n_appartamenti, n_uffici, n_negozi]
        save_data_to_sheet(dati)
