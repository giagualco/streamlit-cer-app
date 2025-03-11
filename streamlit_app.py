import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import folium_static
import pandas as pd

# --- Configurazione della Pagina ---
st.set_page_config(page_title="Gestione Condomini - CER", layout="wide")

# --- Titolo ---
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

# 🔍 Debug: Controlla il formato dei secrets di Streamlit
try:
    credentials_info = json.loads(st.secrets["google_credentials"])
except Exception as e:
    st.error(f"❌ Errore nel parsing del JSON delle credenziali: {e}")
    st.stop()

# --- Autenticazione con Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
gc = gspread.authorize(credentials)

# --- Apertura del Google Sheet ---
spreadsheet = gc.open("Dati_Condomini")  # Assicurati che il nome sia corretto
worksheet = spreadsheet.sheet1

# --- Lettura dei dati ---
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- Visualizzazione della tabella dati ---
st.subheader("📋 Dati dei Condomini")
st.dataframe(df)

# --- Mappa Interattiva ---
st.subheader("📍 Mappa dei Condomini")
mappa = folium.Map(location=[45.07, 7.69], zoom_start=6)  # Centra l'Italia

# Aggiunge i condomini alla mappa
for index, row in df.iterrows():
    if "Latitudine" in row and "Longitudine" in row and row["Latitudine"] and row["Longitudine"]:
        folium.Marker(
            location=[row["Latitudine"], row["Longitudine"]],
            popup=f"{row['Nome Condominio']} - {row['Indirizzo']}",
            tooltip=row["Nome Condominio"]
        ).add_to(mappa)

folium_static(mappa)

# --- Form per aggiungere nuovi dati ---
st.subheader("➕ Aggiungi un Nuovo Condominio")

with st.form("new_condo"):
    nome_condominio = st.text_input("Nome Condominio")
    indirizzo = st.text_input("Indirizzo")
    codice_fiscale = st.text_input("Codice Fiscale")
    riscaldamento = st.selectbox("Riscaldamento Centralizzato?", ["Sì", "No"])
    tipo_riscaldamento = st.selectbox("Tipo di Riscaldamento", ["Pompa di calore", "Ibrido", "Altro"])
    raffreddamento = st.selectbox("Raffreddamento Centralizzato?", ["Sì", "No", "Valutazione in corso"])
    numero_condomini = st.number_input("Numero di Condomini", min_value=1, step=1)
    stato_tetto = st.selectbox("Stato del Tetto", ["Buono", "Medio", "Danneggiato"])
    numero_appartamenti = st.number_input("Numero di Appartamenti", min_value=0, step=1)
    numero_uffici = st.number_input("Numero di Uffici", min_value=0, step=1)
    numero_negozi = st.number_input("Numero di Negozi", min_value=0, step=1)
    latitudine = st.number_input("Latitudine", format="%.6f")
    longitudine = st.number_input("Longitudine", format="%.6f")
    submit = st.form_submit_button("Salva Condominio")

# --- Salvataggio dei dati su Google Sheets ---
if submit:
    nuovo_condominio = [
        nome_condominio, indirizzo, codice_fiscale, riscaldamento, tipo_riscaldamento,
        raffreddamento, numero_condomini, stato_tetto, numero_appartamenti,
        numero_uffici, numero_negozi, latitudine, longitudine
    ]
    worksheet.append_row(nuovo_condominio)
    st.success("✅ Condominio aggiunto con successo!")
    st.experimental_rerun()  # Ricarica l'app per aggiornare i dati
