import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

st.title("Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# 🔹 Caricamento credenziali dai secrets
credentials_info = json.loads(st.secrets["google_credentials"])

# 🔹 Aggiungiamo le scope corrette
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 🔹 Creiamo le credenziali
credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)

# 🔹 Autenticazione con Google Sheets
gc = gspread.authorize(credentials)

# 🔹 Apri il foglio Google Sheets (controlla il nome!)
SHEET_NAME = "Dati_Condomini"
try:
    sheet = gc.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"Errore nell'aprire il foglio: {e}")

# 🔹 Form per inserire dati
with st.form("condominio_form"):
    nome_condominio = st.text_input("Nome Condominio")
    indirizzo = st.text_input("Indirizzo")
    codice_fiscale = st.text_input("Codice Fiscale")
    impianto_riscaldamento = st.selectbox("Riscaldamento Centralizzato?", ["Sì", "No"])
    tipo_riscaldamento = st.selectbox("Tipo di Riscaldamento", ["Pompa di calore", "Ibrido", "Altro"])
    raffreddamento = st.selectbox("Raffreddamento Centralizzato?", ["Sì", "No", "Da Valutare"])
    numero_condomini = st.number_input("Numero di Condomini", min_value=1, step=1)
    stato_tetto = st.selectbox("Stato del Tetto", ["Buono", "Mediocre", "Da Rifare"])
    numero_appartamenti = st.number_input("Numero Appartamenti", min_value=0, step=1)
    numero_uffici = st.number_input("Numero Uffici", min_value=0, step=1)
    numero_negozi = st.number_input("Numero Negozi", min_value=0, step=1)

    submit_button = st.form_submit_button("Salva Dati")

if submit_button:
    try:
        sheet.append_row([nome_condominio, indirizzo, codice_fiscale,
                          impianto_riscaldamento, tipo_riscaldamento, raffreddamento,
                          numero_condomini, stato_tetto,
                          numero_appartamenti, numero_uffici, numero_negozi])
        st.success("✅ Dati salvati correttamente nel Google Sheet!")
    except Exception as e:
        st.error(f"Errore nel salvataggio dei dati: {e}")
