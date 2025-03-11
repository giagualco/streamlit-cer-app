import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

# 🔹 Caricamento delle credenziali dal file JSON nei secrets di Streamlit
credentials_info = json.loads(st.secrets["google_credentials"])

# 🔹 Definizione delle scopes corrette per Google Sheets e Google Drive
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 🔹 Creazione delle credenziali con le nuove scopes
credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)

# 🔹 Connessione a Google Sheets
gc = gspread.authorize(credentials)

# 🔹 Nome del file Google Sheets
SPREADSHEET_NAME = "Dati_Condomini"

# 🔹 Test di accesso a Google Sheets
try:
    # Recupera tutti i fogli disponibili
    spreadsheet_list = gc.openall()
    st.success("✅ Connessione a Google Sheets riuscita!")

    # Verifica se il foglio "Dati_Condomini" esiste
    sheet_names = [sheet.title for sheet in spreadsheet_list]
    if SPREADSHEET_NAME not in sheet_names:
        st.warning(f"⚠️ Il foglio '{SPREADSHEET_NAME}' non esiste. Controlla il nome nel tuo Google Drive.")

    # Apre il foglio
    sheet = gc.open(SPREADSHEET_NAME).sheet1
    st.success(f"📂 Foglio '{SPREADSHEET_NAME}' aperto correttamente!")

except gspread.exceptions.APIError as e:
    st.error(f"Errore di accesso: {e}")
except Exception as e:
    st.error(f"Errore generico: {e}")

# 🔹 Interfaccia Streamlit per testare l'inserimento di dati
st.title("Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

with st.form("condominio_form"):
    nome_condominio = st.text_input("Nome Condominio")
    indirizzo = st.text_input("Indirizzo")
    codice_fiscale = st.text_input("Codice Fiscale")
    impianto_riscaldamento = st.selectbox("Riscaldamento Centralizzato?", ["Sì", "No"])
    tipo_riscaldamento = st.selectbox("Tipo di Riscaldamento", ["Pompa di calore", "Ibrido", "Altro"])
    raffreddamento = st.selectbox("Raffreddamento Centralizzato?", ["Sì", "No", "Da Valutare"])
    numero_condomini = st.number_input("Numero di Condomini", min_value=1, step=1)
    stato_tetto = st.selectbox("Stato del Tetto", ["Buono", "Mediocre", "Da Rifare"])

    # Dati suddivisione unità
    numero_appartamenti = st.number_input("Numero Appartamenti", min_value=0, step=1)
    numero_uffici = st.number_input("Numero Uffici", min_value=0, step=1)
    numero_negozi = st.number_input("Numero Negozi", min_value=0, step=1)

    submit_button = st.form_submit_button("Salva Dati")

# 🔹 Salvataggio dei dati su Google Sheets
if submit_button:
    try:
        new_row = [
            nome_condominio, indirizzo, codice_fiscale,
            impianto_riscaldamento, tipo_riscaldamento, raffreddamento,
            numero_condomini, stato_tetto,
            numero_appartamenti, numero_uffici, numero_negozi
        ]
        sheet.append_row(new_row)
        st.success("✅ Dati salvati correttamente su Google Sheets!")
    except gspread.exceptions.APIError as e:
        st.error(f"Errore nel salvataggio dei dati: {e}")
