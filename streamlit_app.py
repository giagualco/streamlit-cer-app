import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile

# ---- 🔹 Configurazione ----
SHEET_NAME = "Dati_Condomini"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ---- 🔹 Funzione per caricare le credenziali Google ----
@st.cache_resource
def load_google_credentials():
    try:
        credentials_info = json.loads(st.secrets["google_credentials"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(credentials)

        # Autenticazione con PyDrive2 usando Service Account JSON direttamente
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("credentials.json")  # Se hai già un file JSON di credenziali
        if gauth.credentials is None:
            gauth.ServiceAuth()  # Usa il Service Account invece di client_secrets.json

        drive = GoogleDrive(gauth)
        return gc, drive
    except Exception as e:
        st.error(f"❌ Errore di autenticazione con Google: {e}")
        st.stop()

# ---- 🔹 Test di Connessione a Google Sheets ----
def test_google_sheets_connection():
    try:
        gc, _ = load_google_credentials()
        sh = gc.open(SHEET_NAME)
        return sh
    except Exception as e:
        st.error(f"❌ Errore nell'accesso a Google Sheets: {e}")
        st.stop()

# ---- 🔹 Funzione per caricare immagini su Google Drive ----
def upload_image_to_drive(drive, file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(file.getvalue())
            temp_file_path = temp_file.name

        file_drive = drive.CreateFile({'title': file.name})
        file_drive.SetContentFile(temp_file_path)
        file_drive.Upload()
        return f"https://drive.google.com/uc?id={file_drive['id']}"
    
    except Exception as e:
        st.warning(f"⚠️ Errore nel caricamento dell'immagine: {e}")
        return "Nessuna immagine"

# ---- 🔹 UI Streamlit ----
st.title("🏢 Gestione Condomini - Comunità Energetiche Rinnovabili (CER)")
st.write("Compila i dati per registrare un condominio interessato all'installazione di un impianto fotovoltaico.")

# ---- 🔹 Form di Raccolta Dati ----
with st.form("form_dati_condominio"):
    nome_condominio = st.text_input("🏢 Nome del Condominio")
    indirizzo = st.text_input("📍 Indirizzo")
    codice_fiscale = st.text_input("🆔 Codice Fiscale del Condominio")

    st.write("### 🏠 Dati Tecnici dell'Edificio")
    riscaldamento_centralizzato = st.selectbox("🔥 Riscaldamento Centralizzato?", ["Sì", "No"])
    tipo_riscaldamento = st.selectbox("⚡ Tipo di Riscaldamento", ["Pompa di Calore", "Ibrido", "Altro"])
    raffreddamento_centralizzato = st.selectbox("❄️ Raffreddamento Centralizzato?", ["Sì", "No", "Valutazione in corso"])
    stato_tetto = st.selectbox("🏗️ Stato del Tetto", ["Buono", "Da ristrutturare", "Altro"])
    
    num_appartamenti = st.number_input("🏠 Numero Appartamenti", min_value=0, step=1)
    num_uffici = st.number_input("🏢 Numero Uffici", min_value=0, step=1)
    num_negozi = st.number_input("🛒 Numero Negozi", min_value=0, step=1)

    # ---- 🔹 Upload Immagini (Screenshot o Foto del Tetto) ----
    st.write("### 📸 Carica un'immagine del tetto (Screenshot da Google Maps o Foto)")
    immagine_tetto = st.file_uploader("📎 Carica immagine", type=["png", "jpg", "jpeg"])

    # ---- 🔹 Pulsante di invio ----
    submit = st.form_submit_button("📤 Invia Dati")

# ---- 🔹 Invio dei dati a Google Sheets ----
if submit:
    gc, drive = load_google_credentials()
    sh = test_google_sheets_connection()
    ws = sh.sheet1  # Seleziona il primo foglio

    try:
        # ---- 🔹 Caricamento immagine su Google Drive e ottenimento link ----
        immagine_url = upload_image_to_drive(drive, immagine_tetto) if immagine_tetto else "Nessuna immagine"

        # ---- 🔹 Creazione del record da salvare ----
        dati_condominio = [
            nome_condominio, indirizzo, codice_fiscale,
            riscaldamento_centralizzato, tipo_riscaldamento,
            raffreddamento_centralizzato, stato_tetto,
            num_appartamenti, num_uffici, num_negozi,
            immagine_url  # Link dell'immagine su Google Drive
        ]
        ws.append_row(dati_condominio)
        st.success("✅ Dati inviati con successo!")

    except Exception as e:
        st.error(f"❌ Errore nell'invio dei dati: {e}")
