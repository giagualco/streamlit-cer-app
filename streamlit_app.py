import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import folium_static

# Recupero credenziali da Streamlit Secrets
import json
from google.oauth2.service_account import Credentials

credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])


gc = gspread.authorize(credentials)
sheet = gc.open("Dati_Condomini").sheet1  # Assicurati che il foglio esista

# Interfaccia Streamlit
st.title("Gestione Impianti Fotovoltaici per CER")

# Input dati condominio
st.header("Informazioni Condominio")
nome_condominio = st.text_input("Nome Condominio")
indirizzo = st.text_input("Indirizzo")
codice_fiscale = st.text_input("Codice Fiscale")

# Mappa per localizzazione condominio
st.header("Localizzazione su Mappa")
mapa = folium.Map(location=[45.07, 7.69], zoom_start=6)
folium_static(mapa)

# Questionario
st.header("Dati Tecnici del Condominio")
riscaldamento = st.radio("Impianto di riscaldamento centralizzato?", ["Sì", "No"])
tipo_riscaldamento = st.selectbox("Tipo di riscaldamento", ["Pompa di calore", "Ibrido", "Nessuno"], disabled=riscaldamento=="No")
raffreddamento = st.radio("Presenza di raffreddamento centralizzato?", ["Sì", "No", "Lo vorremmo valutare"])
num_condomini = st.number_input("Numero di condomini presenti", min_value=1, step=1)
num_appartamenti = st.number_input("Numero di appartamenti", min_value=0, step=1)
num_uffici = st.number_input("Numero di uffici", min_value=0, step=1)
num_negozi = st.number_input("Numero di negozi", min_value=0, step=1)
stato_tetto = st.selectbox("Stato del tetto", ["Buono", "Da ristrutturare", "Non valutato"])

# Invio dati a Google Sheets
if st.button("Salva i dati"):
    dati = [nome_condominio, indirizzo, codice_fiscale, riscaldamento, tipo_riscaldamento, raffreddamento, num_condomini, num_appartamenti, num_uffici, num_negozi, stato_tetto]
    sheet.append_row(dati)
    st.success("Dati salvati con successo su Google Sheets!")
