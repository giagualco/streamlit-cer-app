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

# ---- Funzione per caricare credenziali ----
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

# ---- Funzione per ottenere coordinate da un indirizzo ----
def get_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit-app", timeout=10)
    location = geolocator.geocode(address)
    return [location.latitude, location.longitude] if location else None

# ---- UI Streamlit ----
st.title("🏢 Rilevamento Condomini - Comunità Energetiche Rinnovabili (CER)")
st.write("Individua il condominio sulla mappa e **trascina il PIN** sul tetto.")

# ---- Sezione MAPPA ----
st.subheader("🔍 Cerca un indirizzo (Nominatim)")
indirizzo = st.text_input("Inserisci l'indirizzo del condominio")
cerca = st.button("📍 Trova indirizzo")

# Creazione della mappa con vista satellitare gratuita
m = folium.Map(
    location=[45.0703, 7.6869],
    zoom_start=16,
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap"
)

# Aggiunta di strumenti alla mappa
LocateControl().add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)

# Se l'utente cerca un indirizzo, aggiorniamo la mappa
if cerca and indirizzo:
    with st.spinner("🔍 Ricerca in corso..."):
        coords = get_coordinates(indirizzo)
        if coords:
            folium.Marker(
                location=coords, 
                popup="Trascina il PIN sul tetto",
                draggable=True,
                icon=folium.Icon(color="red")
            ).add_to(m)
            m.location = coords
        else:
            st.error("❌ Indirizzo non trovato, prova con una via più specifica.")

# Istruzioni utente
st.markdown("➡️ **Istruzioni:** Cerca un indirizzo, poi **trascina il PIN** sul tetto del condominio.")

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
