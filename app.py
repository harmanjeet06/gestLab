import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GestLab Cloud Secure", layout="wide", initial_sidebar_state="expanded")

# --- CSS INIETTATO PER FORZARE I COLORI REALI DEI PULSANTI ---
st.markdown("""
<style>
    /* Forza il colore VERDE per i pulsanti LIBERO */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #28a745 !important;
    }
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #218838 !important;
        color: white !important;
    }
    /* Forza il colore ROSSO per i pulsanti OCCUPATO */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: 1px solid #dc3545 !important;
    }
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #c82333 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONNESSIONE A GOOGLE SHEETS ---
GOOGLE_SHEET_ID = "1T83Ofmcesg_YoYbKkLHM1LFaw0c72AHwo9QTPyIb0kM"
URL_UTENTI = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=utenti"
URL_STUDENTI = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=studenti"

@st.cache_data(ttl=60)
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
        return {}

@st.cache_data(ttl=60)
def carica_classi_da_sheets():
    try:
        df = pd.read_csv(URL_STUDENTI)
        return df["classe"].dropna().astype(str).tolist()
    except Exception as e:
        return []

# --- INIZIALIZZAZIONE MEMORIA DI SESSIONE (STATO PERSISTENTE) ---
if "autenticato" not in st.session_state: st.session_state.autenticato = False
if "ruolo" not in st.session_state: st.session_state.ruolo = None
if "utente_attivo" not in st.session_state: st.session_state.utente_attivo = None

# Memoria globale per non perdere i dati ai click
if "prenotazioni" not in st.session_state: st.session_state.prenotazioni = {}
if "scambi" not in st.session_state: st.session_state.scambi = []
if "manutenzioni" not in st.session_state: st.session_state.manutenzioni = {}

# Variabili di memoria per i click sul tabellone
if "lab_selezionato_click" not in st.session_state: st.session_state.lab_selezionato_click = "Info"
if "ora_selezionata_click" not in st.session_state: st.session_state.ora_selezionata_click = "1ª ora"

dizionario_utenti = carica_utenti_da_sheets()
elenco_classi = carica_classi_da_sheets()

GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]
LABORATORI = ["Info", "AutoCAD", "Sistel"]

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
    scelta_accesso = st.radio("Scegli come accreditarti:", ["Docente / Personale Tecnico", "Studente (Consulta Orari)"])
    
    if scelta_accesso == "Docente / Personale Tecnico":
        with st.form("form_login"):
            username_input = st.text_input("Username scolastico:")
            password_input = st.text_input("Password:", type="password")
            pulsante_login = st.form_submit_button("Effettua Login")
            
            if pulsante_login:
                user_clean = username_input.strip()
                pass_clean = password_input.strip()
                
                if user_clean == "admin" and pass_clean == "admin":
                    st.session_state.autenticato = True
                    st.session_state.ruolo = "Tecnico / Amministratore"
                    st.session_state.utente_attivo = "Admin Supremo"
                    st.rerun()
                elif user_clean in dizionario_utenti and dizionario_utenti[user_clean]["password"] == pass_clean:
                    st.session_state.autenticato = True
                    st.session_state.ruolo = dizionario_utenti[user_clean]["ruolo"]
                    st.session_state.utente_attivo = dizionario_utenti[user_clean]["nominativo"]
                    st.rerun()
                else:
                    st.error("Credenziali non corrette.")
                    
    else:
        with st.form("form_studenti"):
            classe_selezionata = st.selectbox("Seleziona la tua Classe:", elenco_classi)
            if st.form_submit_button("Accedi al Tabellone"):
                st.session_state.autenticato = True
                st.session_state.ruolo = "Studente"
                st.session_state.utente_attivo = f"Studente ({classe_selezionata})"
                st.rerun()

# ==========================================
# APPLICAZIONE ATTIVA
# ==========================================
else:
    ruolo = st.session_state.ruolo
    utente_attivo = st.session_state.utente_attivo

    st.sidebar.title("🧬 GestLab v1.3")
    st.sidebar.write(f"Utente: **{utente_attivo}**")
    st.sidebar.write(f"Ruolo: `{ruolo}`")
    
    if st.sidebar.button("🚪 Esci dal sistema"):
        st.session_state.autenticato = False
        st.rerun()
        
    if st.sidebar.button("🔄 Forza Aggiornamento Database"):
        st.cache_data.clear()
        st.rerun()

    st.title("🖥️ Tabellone Orari e Prenotazione Laboratori")
    st.divider()

    col_data1, col_data2 = st.columns([1, 3])
    with col_data1:
        data_selezionata = st.date_input("Seleziona Data:", datetime.date.today())
        giorni_settimana_eng = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        giorno_testo = giorni_settimana_eng[data_selezionata.weekday()]

    with col_data2:
        st.subheader(f"📅 Giorno: {giorno_testo} {data_selezionata.strftime('%d/%m/%Y')}")

    if giorno_testo in GIORNI:
        schema_orario = get_orari_per_giorno(giorno_testo)

        st.write("### 📊 Tabellone di Stato")
        
        col_orari, col_l1, col_l2, col_l3 = st.columns([3, 3, 3, 3])
        with col_orari: st.markdown("**🕒 Ora / Fascia**")
        with col_l1: st.markdown("**💻 Laboratorio Info**")
        with col_l2: st.markdown("**📐 Laboratorio AutoCAD**")
        with col_l3: st.markdown("**🔌 Laboratorio Sistel**")
        st.divider()

        # COSTRUZIONE RIGIDA DELLA GRIGLIA
        for slot in schema_orario:
            riga_ora, riga_l1, riga_l2, riga_l3 = st.columns([3, 3, 3, 3])
            
            with riga_ora:
                st.write(f"**{slot['ora']}** \n({slot['inizio']} - {slot['fine']})")
            
            for i_lab, laboratorio in enumerate(LABORATORI):
                colonna_corrente = [riga_l1, riga_l2, riga_l3][i_lab]
                chiave = (data_selezionata, laboratorio, slot['ora'])
                
                with colonna_corrente:
                    if not slot['prenotabile']:
                        st.button("☕ Intervallo", key=f"int_{laboratorio}_{slot['ora']}", disabled=True, use_container_width=True)
                    
                    elif chiave in st.session_state.manutenzioni:
                        st.button(f"🔧 MANUTENZIONE", key=f"btn_{chiave}", disabled=True, use_container_width=True)
                    
                    elif chiave in st.session_state.prenotazioni:
                        proprietario = st.session_state.prenotazioni[chiave]['prof']
                        motivo_pren = st.session_state.prenotazioni[chiave]['motivo']
                        
                        # Tasto occupato (Colore Rosso forzato da CSS tramite type="secondary")
                        if st.button(f"🔴 {proprietario[:10]} ({motivo_pren[:10]})", key=f"btn_{chiave}", type="secondary", use_container_width=True):
                            if ruolo == "Professore" and proprietario != utente_attivo:
                                st.session_state.lab_selezionato_click = laboratorio
                                st.session_state.ora_selezionata_click = slot['ora']
                                st.rerun()
                    else:
                        # Tasto libero (Colore Verde forzato da CSS tramite type="primary")
                        if st.button("🟢 LIBERO", key=f"btn_{chiave}", type="primary", use_container_width=True):
                            if ruolo in ["Professore", "Tecnico / Amministratore"]:
                                st.session_state.lab_selezionato_click = laboratorio
                                st.session_state.ora_selezionata_click = slot['ora']
                                st.rerun()
            st.write("---")

        # ==========================================
        # AREA OPERATIVA (PERSISTENTE E AGGIORNATA)
        # ==========================================
        st.write("### ⚙️ Area Operativa")
        st.info(f"📍 Selezionato nel tabellone: **{st.session_state.lab_selezionato_click}** alla **{st.session_state.ora_selezionata_click}**")

        if ruolo == "Professore":
            tab1, tab2, tab3 = st.tabs(["🆕 Nuova Prenotazione", "🔄 Richiedi Scambio", "📋 Mie Prenotazioni"])
            
            with tab1:
                st.write("#### Inserisci i dettagli per bloccare l'aula:")
                # I selettori leggono il valore salvato nella sessione
                lab_scelto = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click), key="sel_l")
                ore_disp = [s['ora'] for s in schema_orario if s['prenotabile']]
                ora_scelta = st.selectbox("Ora:", ore_disp, index=ore_disp.index(st.session_state.ora_selezionata_click), key="sel_o")
                motivo = st.text_input("Classe / Materia (Es: 5A - Sistemi):", key="act")
                
                if st.button("Salva sul Tabellone", type="primary", key="save_p"):
                    chiave_pren = (data_selezionata, lab_scelto, ora_scelta)
                    if chiave_pren in st.session_state.prenotazioni:
                        st.error("Questo slot è stato occupato un attimo fa!")
                    elif motivo.strip() == "":
                        st.warning("Devi scrivere la classe/materia prima di salvare.")
                    else:
                        # Salviamo nella sessione sicura!
                        st.session_state.prenotazioni[chiave_pren] = {"prof": utente_attivo, "motivo": motivo}
                        st.success("Prenotazione registrata con successo!")
                        st.rerun()

            with tab2:
                st.subheader("Invia proposta di scambio")
                lab_scambio = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click), key="s_l")
                ora_scambio = st.selectbox("Ora:", [s['ora'] for s in schema_orario if s['prenotabile']], index=[s['ora'] for s in schema_orario if s['prenotabile']].index(st.session_state.ora_selezionata_click), key="s_o")
                chiave_scambio = (data_selezionata, lab_scambio, ora_scambio)
                
                if chiave_scambio in st.session_state.prenotazioni:
                    prof_dest = st.session_state.prenotazioni[chiave_scambio]['prof']
                    if prof_dest != utente_attivo:
                        st.write(f"Destinatario richiesta: **{prof_dest}**")
                        msg = st.text_area("Messaggio per il collega:")
                        if st.button("Spedisci richiesta", key="send_s"):
                            st.session_state.scambi.append({"da_prof": utente_attivo, "a_prof": prof_dest, "data": data_selezionata, "lab": lab_scambio, "ora": ora_scambio, "messaggio": msg, "stato": "In attesa"})
                            st.success("Richiesta inviata!")
                else:
                    st.info("Questo slot è vuoto. Usa il primo pannello per prenderlo subito.")

            with tab3:
                st.subheader("Le tue prenotazioni di oggi")
                elenco_mie = [k for k, v in st.session_state.prenotazioni.items() if v["prof"] == utente_attivo]
                if not elenco_mie:
                    st.write("Nessuna prenotazione effettuata per oggi.")
                for k in elenco_mie:
                    st.write(f"• **{k[1]}** alla **{k[2]}** -> *{st.session_state.prenotazioni[k]['motivo']}*")
                    if st.button("Elimina ed eliditi dello slot", key=f"del_{k[1]}_{k[2]}"):
                        del st.session_state.prenotazioni[k]
                        st.rerun()

        elif ruolo == "Studente":
            st.subheader("🔍 Cerca la tua Aula")
            testo_cercato = st.text_input("Cerca Classe o Materia:")
            if testo_cercato:
                trovato = False
                for k, v in st.session_state.prenotazioni.items():
                    if testo_cercato.lower() in v["motivo"].lower() and k[0] == data_selezionata:
                        st.write(f"📖 **{k[1]}** | Ora: **{k[2]}** -> Lezione di: {v['motivo']} ({v['prof']})")
                        trovato = True
                if not trovato:
                    st.write("Nessuna lezione trovata.")

        elif ruolo == "Tecnico / Amministratore":
            st.subheader("🔧 Gestione Manutenzioni")
            lab_m = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click))
            ora_m = st.selectbox("Ora:", [s['ora'] for s in schema_orario if s['prenotabile']], index=[s['ora'] for s in schema_orario if s['prenotabile']].index(st.session_state.ora_selezionata_click))
            motivo_m = st.text_input("Specifiche del Guasto:")
            
            if st.button("Attiva Blocco Laboratorio", type="primary"):
                if motivo_m.strip():
                    chiave_m = (data_selezionata, lab_m, ora_m)
                    if chiave_m in st.session_state.prenotazioni:
                        del st.session_state.prenotazioni[chiave_m]
                    st.session_state.manutenzioni[chiave_m] = motivo_m
                    st.success("Laboratorio bloccato!")
                    st.rerun()
