import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

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

# ---- UI Streamlit ----
st.title("🏢 Rilevamento Condomini - Comunità Energetiche Rinnovabili (CER)")
st.write("Compila il modulo e carica uno **screenshot di Google Maps** o una **foto del tetto**.")

# ---- Sezione MODULO RACCOLTA DATI ----
st.subheader("📋 Inserisci i dati del condominio")

nome_condominio = st.text_input("Nome del condominio")
indirizzo = st.text_input("Indirizzo completo del condominio")
riscaldamento = st.selectbox("Tipo di riscaldamento", ["Centralizzato", "Autonomo", "Nessuno"])
tipo_riscaldamento = st.selectbox("Tipologia", ["Gas", "Pompa di calore", "Ibrido"], disabled=(riscaldamento == "Nessuno"))
raffrescamento = st.selectbox("Raffrescamento centralizzato", ["Sì", "No"])
n_condomini = st.number_input("Numero di condomini", min_value=1, step=1)
stato_tetto = st.selectbox("Stato del tetto", ["Buono", "Mediocre", "Da rifare"])
n_appartamenti = st.number_input("Numero di appartamenti", min_value=1, step=1)
n_uffici = st.number_input("Numero di uffici", min_value=0, step=1)
n_negozi = st.number_input("Numero di negozi", min_value=0, step=1)

# ---- Sezione UPLOAD IMMAGINE ----
st.subheader("📸 Carica un'immagine del tetto")
uploaded_file = st.file_uploader("Carica uno screenshot di Google Maps o una foto del tetto", type=["jpg", "png", "jpeg"])

# ---- INVIA DATI ----
if st.button("📤 Invia dati"):
    if not nome_condominio or not indirizzo or not uploaded_file:
        st.warning("⚠️ Devi inserire tutti i dati e caricare un'immagine!")
    else:
        dati = [
            nome_condominio, indirizzo, riscaldamento, tipo_riscaldamento, raffrescamento,
            n_condomini, stato_tetto, n_appartamenti, n_uffici, n_negozi, uploaded_file.name
        ]
        save_data_to_sheet(dati)
