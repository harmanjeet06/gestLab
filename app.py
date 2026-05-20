import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GestLab Cloud Secure", layout="wide", initial_sidebar_state="expanded")

# --- CONNESSIONE A GOOGLE SHEETS (VIA URL CSV PUBBLICO) ---
# ID inserito con successo!
GOOGLE_SHEET_ID = "1T83Ofmcesg_YoYbKkLHM1LFaw0c72AHwo9QTPyIb0kM"

URL_UTENTI = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=utenti"
URL_STUDENTI = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=studenti"

@st.cache_data(ttl=60)  # Mantiene i dati in memoria per 60 secondi per evitare continui sovraccarichi di richieste a Google
def carica_utenti_da_sheets():
    try:
        df = pd.read_csv(URL_UTENTI)
        utenti = {}
        for _, row in df.iterrows():
            utenti[str(row["username"]).strip()] = {
                "password": str(row["password"]).strip(),
                "ruolo": str(row["ruolo"]).strip(),
                "nominativo": str(row["nominativo"]).strip()
            }
        return utenti
    except Exception as e:
        st.error(f"Errore nel caricamento degli utenti da Google Sheets: {e}")
        return {}

@st.cache_data(ttl=60)
def carica_classi_da_sheets():
    try:
        df = pd.read_csv(URL_STUDENTI)
        return df["classe"].dropna().astype(str).tolist()
    except Exception as e:
        st.error(f"Errore nel caricamento delle classi da Google Sheets: {e}")
        return []

# --- INIZIALIZZAZIONE DELLA SESSIONE (SICUREZZA RUOLI) ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "ruolo" not in st.session_state:
    st.session_state.ruolo = None
if "utente_attivo" not in st.session_state:
    st.session_state.utente_attivo = None

# Database temporaneo in memoria per le prenotazioni del giorno corrente
if "prenotazioni" not in st.session_state:
    st.session_state.prenotazioni = {}
if "scambi" not in st.session_state:
    st.session_state.scambi = []
if "manutenzioni" not in st.session_state:
    st.session_state.manutenzioni = {}

# Scarichiamo i dati dal Cloud di Google
dizionario_utenti = carica_utenti_da_sheets()
elenco_classi = carica_classi_da_sheets()

# --- COSTRUTTORE STRUTTURA ORARI ---
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]
LABORATORI = ["Sistel Info", "AutoCAD"]

def get_orari_per_giorno(giorno):
    if giorno in ["Martedì", "Venerdì"]:
        return [
            {"ora": "1ª ora", "inizio": "08:00", "fine": "08:50", "prenotabile": True},
            {"ora": "2ª ora", "inizio": "08:50", "fine": "09:40", "prenotabile": True},
            {"ora": "3ª ora", "inizio": "09:40", "fine": "10:30", "prenotabile": True},
            {"ora": "Intervallo", "inizio": "10:30", "fine": "10:45", "prenotabile": False},
            {"ora": "4ª ora", "inizio": "10:45", "fine": "11:35", "prenotabile": True},
            {"ora": "5ª ora", "inizio": "11:35", "fine": "12:25", "prenotabile": True},
            {"ora": "6ª ora", "inizio": "12:25", "fine": "13:15", "prenotabile": True},
        ]
    else:
        return [
            {"ora": "1ª ora", "inizio": "08:00", "fine": "09:00", "prenotabile": True},
            {"ora": "2ª ora", "inizio": "09:00", "fine": "10:00", "prenotabile": True},
            {"ora": "3ª ora", "inizio": "10:00", "fine": "10:55", "prenotabile": True},
            {"ora": "Intervallo", "inizio": "10:55", "fine": "11:10", "prenotabile": False},
            {"ora": "4ª ora", "inizio": "11:10", "fine": "12:10", "prenotabile": True},
            {"ora": "5ª ora", "inizio": "12:10", "fine": "13:10", "prenotabile": True},
        ]

# ==========================================
# SCHERMATA DI LOGIN
# ==========================================
if not st.session_state.autenticato:
    st.title("🔐 Accesso Centrale - GestLab")
    st.write("I dati di accesso sono verificati in tempo reale su Google Sheets Database.")
    
    scelta_accesso = st.radio("Scegli come accreditarti:", ["Docente / Personale Tecnico", "Studente (Consulta Orari)"])
    
    if scelta_accesso == "Docente / Personale Tecnico":
        with st.form("form_login"):
            username_input = st.text_input("Username scolastico:")
            password_input = st.text_input("Password:", type="password")
            pulsante_login = st.form_submit_button("Effettua Login")
            
            if pulsante_login:
                user_clean = username_input.strip()
                if user_clean in dizionario_utenti and dizionario_utenti[user_clean]["password"] == password_input.strip():
                    st.session_state.autenticato = True
                    st.session_state.ruolo = dizionario_utenti[user_clean]["ruolo"]
                    st.session_state.utente_attivo = dizionario_utenti[user_clean]["nominativo"]
                    st.success("Autenticato con successo!")
                    st.rerun()
                else:
                    st.error("Credenziali non corrette. Verifica i dati sul Foglio Google.")
                    
    else:  # Studente
        with st.form("form_studente"):
            if not elenco_classi:
                st.warning("Caricamento classi da Google Sheets in corso...")
            classe_selezionata = st.selectbox("Seleziona la tua Classe (Verificata da Cloud):", elenco_classi)
            pulsante_studente = st.form_submit_button("Accedi al Tabellone")
            
            if pulsante_studente:
                st.session_state.autenticato = True
                st.session_state.ruolo = "Studente"
                st.session_state.utente_attivo = f"Studente ({classe_selezionata})"
                st.success("Benvenuto Studente!")
                st.rerun()

# ==========================================
# APPLICAZIONE (AUTENTICATA DA SESSIONE)
# ==========================================
else:
    ruolo = st.session_state.ruolo
    utente_attivo = st.session_state.utente_attivo

    st.sidebar.title("🧬 GestLab v1.2")
    st.sidebar.subheader("🔒 Sessione Sicura")
    st.sidebar.write(f"Utente: **{utente_attivo}**")
    st.sidebar.write(f"Ruolo: `{ruolo}`")
    
    if st.sidebar.button("🚪 Esci dal sistema"):
        st.session_state.autenticato = False
        st.session_state.ruolo = None
        st.session_state.utente_attivo = None
        st.rerun()
        
    st.sidebar.divider()
    if st.sidebar.button("🔄 Forza Aggiornamento Database"):
        st.cache_data.clear()  # Svuota la cache locale di Streamlit obbligandolo a ricaricare i dati da Google Sheets
        st.sidebar.success("Dati aggiornati dal Cloud!")
        st.rerun()

    st.title("🖥️ Tabellone Orari e Prenotazione Laboratori")
    st.divider()

    # SELEZIONE DATA
    col_data1, col_data2 = st.columns([1, 3])
    with col_data1:
        data_selezionata = st.date_input("Seleziona Data:", datetime.date.today())
        giorni_settimana_eng = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        giorno_testo = giorni_settimana_eng[data_selezionata.weekday()]

    with col_data2:
        st.subheader(f"📅 Giorno: {giorno_testo} {data_selezionata.strftime('%d/%m/%Y')}")
        if giorno_testo in ["Sabato", "Domenica"]:
            st.warning("Laboratori chiusi nel fine settimana.")

    if giorno_testo in GIORNI:
        schema_orario = get_orari_per_giorno(giorno_testo)

        st.write("### 📊 Disponibilità attuale slot orari")
        col_orari, col_lab1, col_lab2 = st.columns([2, 4, 4])
        
        with col_orari:
            st.write("**Ora / Fascia**")
            for slot in schema_orario:
                st.write(f"🕒 **{slot['ora']}** ({slot['inizio']} - {slot['fine']})")
                
        with col_lab1:
            st.write(f"🟩 **{LABORATORI[0]}**")
            for slot in schema_orario:
                chiave = (data_selezionata, LABORATORI[0], slot['ora'])
                if not slot['prenotabile']: st.info("☕ Intervallo")
                elif chiave in st.session_state.manutenzioni: st.error(f"🔧 MANUTENZIONE: {st.session_state.manutenzioni[chiave]}")
                elif chiave in st.session_state.prenotazioni: st.warning(f"🔴 Occupato da {st.session_state.prenotazioni[chiave]['prof']}")
                else: st.success("🟢 Libero")

        with col_lab2:
            st.write(f"📐 **{LABORATORI[1]}**")
            for slot in schema_orario:
                chiave = (data_selezionata, LABORATORI[1], slot['ora'])
                if not slot['prenotabile']: st.info("☕ Intervallo")
                elif chiave in st.session_state.manutenzioni: st.error(f"🔧 MANUTENZIONE: {st.session_state.manutenzioni[chiave]}")
                elif chiave in st.session_state.prenotazioni: st.warning(f"🔴 Occupato da {st.session_state.prenotazioni[chiave]['prof']}")
                else: st.success("🟢 Libero")

        st.divider()

        if ruolo == "Professore":
            tab1, tab2, tab3 = st.tabs(["🆕 Nuova Prenotazione", "🔄 Richiedi Scambio", "📋 Mie Prenotazioni"])
            
            with tab1:
                st.subheader("Blocca un laboratorio")
                lab_scelto = st.selectbox("Seleziona Laboratorio:", LABORATORI)
                ore_disponibili = [slot['ora'] for slot in schema_orario if slot['prenotabile']]
                ora_scelta = st.selectbox("Seleziona Ora:", ore_disponibili)
                motivo = st.text_input("Attività didattica prevista (Classe / Materia):")
                
                if st.button("Salva Prenotazione", type="primary"):
                    chiave_pren = (data_selezionata, lab_scelto, ora_scelta)
                    if chiave_pren in st.session_state.manutenzioni: st.error("Laboratorio bloccato dal tecnico.")
                    elif chiave_pren in st.session_state.prenotazioni: st.error("Slot già occupato da un altro docente.")
                    elif motivo.strip() == "": st.warning("Inserisci l'attività.")
                    else:
                        st.session_state.prenotazioni[chiave_pren] = {"prof": utente_attivo, "motivo": motivo}
                        st.success("Registrato con successo!")
                        st.rerun()

            with tab2:
                st.subheader("Invia proposta di scambio")
                lab_scambio = st.selectbox("Laboratorio oggetto dello scambio:", LABORATORI, key="s_l")
                ora_scambio = st.selectbox("Ora:", [slot['ora'] for slot in schema_orario if slot['prenotabile']], key="s_o")
                chiave_scambio = (data_selezionata, lab_scambio, ora_scambio)
                if chiave_scambio in st.session_state.prenotazioni:
                    prof_dest = st.session_state.prenotazioni[chiave_scambio]['prof']
                    if prof_dest != utente_attivo:
                        st.write(f"Slot occupato attualmente da: **{prof_dest}**")
                        msg = st.text_area("Messaggio cordiale per lo scambio:")
                        if st.button("Spedisci richiesta di scambio"):
                            st.session_state.scambi.append({"da_prof": utente_attivo, "a_prof": prof_dest, "data": data_selezionata, "lab": lab_scambio, "ora": ora_scambio, "messaggio": msg, "stato": "In attesa"})
                            st.success("Richiesta recapitata nel sistema.")
                else:
                    st.info("Lo slot è vuoto, puoi prenderlo subito senza scambi.")

            with tab3:
                st.subheader("Riepilogo ore prenotate a tuo nome")
                for k, v in list(st.session_state.prenotazioni.items()):
                    if v["prof"] == utente_attivo:
                        st.write(f"• **{k[0].strftime('%d/%m/%Y')}** alla {k[2]} su {k[1]} (*{v['motivo']}*)")
                        if st.button("Cancella", key=f"d_{k}"):
                            del st.session_state.prenotazioni[k]
                            st.rerun()

        elif ruolo == "Studente":
            st.subheader("🔍 Motore di ricerca rapida aule per studenti")
            st.info("Benvenuto. Puoi cercare dove si trova una determinata materia o classe inserendola qui sotto.")
            testo_cercato = st.text_input("Inserisci stringa di ricerca (es. 5A o Sistemi):")
            if testo_cercato:
                trovato = False
                for k, v in st.session_state.prenotazioni.items():
                    if testo_cercato.lower() in v["motivo"].lower():
                        st.write(f"📖 Il giorno **{k[0].strftime('%d/%m/%Y')}** alla **{k[2]}** la classe è nel laboratorio **{k[1]}** (Docente: {v['prof']})")
                        trovato = True
                if not trovato:
                    st.write("Nessuna lezione trovata con questi criteri.")

        elif ruolo == "Tecnico / Amministratore":
            st.subheader("🔧 Gestione Sospensioni Tecniche / Manutenzioni Hardware")
            lab_m = st.selectbox("Laboratorio:", LABORATORI)
            ora_m = st.selectbox("Fascia oraria del blocco:", [slot['ora'] for slot in schema_orario if slot['prenotabile']])
            motivo_m = st.text_input("Natura del guasto o intervento:")
            
            if st.button("Applica Sospensione Laboratorio", type="primary"):
                if motivo_m.strip():
                    chiave_m = (data_selezionata, lab_m, ora_m)
                    if chiave_m in st.session_state.prenotazioni:
                        del st.session_state.prenotazioni[chiave_m]
                    st.session_state.manutenzioni[chiave_m] = motivo_m
                    st.success("Laboratorio isolato e bloccato.")
                    st.rerun()
