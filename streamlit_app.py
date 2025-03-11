import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
import gspread
from geopy.geocoders import Nominatim
from folium.plugins import LocateControl, MeasureControl, Search

# Definizione delle credenziali Google
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def load_google_credentials():
    """Carica le credenziali di Google"""
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception:
        st.error("Errore di autenticazione con Google. Controlla le credenziali.")
        st.stop()

# Configurazione del foglio Google Sheets
SHEET_NAME = "Dati_Condomini"
gc = load_google_credentials()
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1

# ---- UI Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")
st.markdown("### Individua il condominio, inserisci i dati e invia il modulo.")

# ---- SEZIONE MAPPA ----
st.subheader("📍 Seleziona il condominio sulla mappa")

# Mappa con sfondo satellitare
m = folium.Map(
    location=[45.0703, 7.6869], zoom_start=15,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri"
)

# Aggiungere strumenti alla mappa
LocateControl(auto_start=False).add_to(m)
MeasureControl(primary_length_unit='meters').add_to(m)

# Barra di ricerca per individuare un indirizzo
Search(
    layer=m, 
    search_label="Indirizzo",
    placeholder="Cerca un indirizzo",
    collapsed=False
).add_to(m)

# Mostra la mappa e permette all'utente di aggiungere un PIN
map_data = st_folium(m, width=850, height=550)

# Verifica se l'utente ha selezionato un punto sulla mappa
latitude, longitude = None, None
if map_data and map_data["last_clicked"]:
    latitude = map_data["last_clicked"]["lat"]
    longitude = map_data["last_clicked"]["lng"]
    st.success(f"📍 Coordinate selezionate: {latitude}, {longitude}")

# ---- SEZIONE MODULO ----
st.subheader("📋 Compila i dati del condominio")
with st.form("dati_condominio"):
    indirizzo = st.text_input("📍 Indirizzo del condominio")
    num_appartamenti = st.number_input("🏠 Numero di appartamenti", min_value=0, step=1)
    num_uffici = st.number_input("🏢 Numero di uffici", min_value=0, step=1)
    num_negozi = st.number_input("🛍 Numero di negozi", min_value=0, step=1)

    tipo_riscaldamento = st.selectbox("🔥 Tipo di riscaldamento", ["Centralizzato", "Pompa di calore", "Altro"])
    raffreddamento = st.selectbox("❄️ Raffreddamento centralizzato?", ["Sì", "No", "Valutazione in corso"])
    stato_tetto = st.selectbox("🏗️ Stato del tetto", ["Buono", "Da ristrutturare", "Invalutabile"])

    submit_button = st.form_submit_button("📤 Invia Dati")

# ---- SALVATAGGIO DATI ----
if submit_button:
    if latitude and longitude:
        # Salva i dati in Google Sheets
        worksheet.append_row([
            indirizzo, latitude, longitude, num_appartamenti, num_uffici, num_negozi,
            tipo_riscaldamento, raffreddamento, stato_tetto
        ])
        st.success("✅ Dati inviati con successo!")
    else:
        st.warning("⚠️ Seleziona un punto sulla mappa prima di inviare il modulo!")
