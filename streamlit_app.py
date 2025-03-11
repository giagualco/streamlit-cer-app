import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Impostazioni API Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Caricamento delle credenziali
credentials_info = st.secrets["google_credentials"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

# Connessione a Google Sheets
gc = gspread.authorize(credentials)
sheet = gc.open("Dati_Condomini").sheet1

def carica_dati():
    """Carica i dati dal Google Sheet."""
    data = sheet.get_all_records()
    return pd.DataFrame(data)

st.title("Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")

df = carica_dati()
st.write(df)
