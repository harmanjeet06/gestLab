import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GestLab Cloud Secure", layout="wide", initial_sidebar_state="expanded")

# --- CSS PER I COLORI REALI DEI PULSANTI ---
st.markdown("""
<style>
    /* VERDE per i pulsanti LIBERO */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #28a745 !important;
    }
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #218838 !important;
    }
    /* ROSSO per i pulsanti OCCUPATO / TUO */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: 1px solid #dc3545 !important;
    }
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #c82333 !important;
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
    except:
        return {}

@st.cache_data(ttl=60)
def carica_classi_da_sheets():
    try:
        df = pd.read_csv(URL_STUDENTI)
        return df["classe"].dropna().astype(str).tolist()
    except:
        return []

# --- INIZIALIZZAZIONE MEMORIA STATO PERSISTENTE ---
if "autenticato" not in st.session_state: st.session_state.autenticato = False
if "ruolo" not in st.session_state: st.session_state.ruolo = None
if "utente_attivo" not in st.session_state: st.session_state.utente_attivo = None

if "prenotazioni" not in st.session_state: st.session_state.prenotazioni = {}
if "manutenzioni" not in st.session_state: st.session_state.manutenzioni = {}

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

# --- FUNZIONI DI CALLBACK PER AZIONI IMMEDIATE AL CLICK ---
def esegui_prenotazione(chiave, prof):
    st.session_state.prenotazioni[chiave] = {"prof": prof, "motivo": "Lezione Didattica"}

def cancella_prenotazione(chiave):
    if chiave in st.session_state.prenotazioni:
        del st.session_state.prenotazioni[chiave]

def gestisci_manutenzione(chiave, azione):
    if azione == "attiva":
        if chiave in st.session_state.prenotazioni:
            del st.session_state.prenotazioni[chiave]
        st.session_state.manutenzioni[chiave] = "Sospensione Tecnica"
    elif azione == "disattiva":
        if chiave in st.session_state.manutenzioni:
            del st.session_state.manutenzioni[chiave]

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
            if st.form_submit_button("Effettua Login"):
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
                    st.error("Credenziali errate.")
    else:
        with st.form("form_studenti"):
            classe_selezionata = st.selectbox("Seleziona la tua Classe:", elenco_classi)
            if st.form_submit_button("Accedi al Tabellone"):
                st.session_state.autenticato = True
                st.session_state.ruolo = "Studente"
                st.session_state.utente_attivo = f"Studente ({classe_selezionata})"
                st.rerun()

# ==========================================
# APPLICAZIONE ATTIVA (ONE-CLICK REAL WORKING)
# ==========================================
else:
    ruolo = st.session_state.ruolo
    utente_attivo = st.session_state.utente_attivo

    st.sidebar.title("🧬 GestLab v1.5")
    st.sidebar.write(f"Utente: **{utente_attivo}**")
    st.sidebar.write(f"Ruolo: `{ruolo}`")
    
    if st.sidebar.button("🚪 Esci"):
        st.session_state.autenticato = False
        st.rerun()
    if st.sidebar.button("🔄 Aggiorna DB"):
        st.cache_data.clear()
        st.rerun()

    st.title("🖥️ Tabellone Orari Interattivo")
    st.divider()

    data_selezionata = st.date_input("Seleziona Data:", datetime.date.today())
    giorni_settimana_eng = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    giorno_testo = giorni_settimana_eng[data_selezionata.weekday()]

    st.subheader(f"📅 {giorno_testo} {data_selezionata.strftime('%d/%m/%Y')}")

    if giorno_testo in GIORNI:
        schema_orario = get_orari_per_giorno(giorno_testo)

        col_orari, col_l1, col_l2, col_l3 = st.columns([3, 3, 3, 3])
        with col_orari: st.markdown("**🕒 Ora / Fascia**")
        with col_l1: st.markdown("**💻 Info**")
        with col_l2: st.markdown("**📐 AutoCAD**")
        with col_l3: st.markdown("**🔌 Sistel**")
        st.divider()

        for slot in schema_orario:
            riga_ora, riga_l1, riga_l2, riga_l3 = st.columns([3, 3, 3, 3])
            
            with riga_ora:
                st.write(f"**{slot['ora']}** \n({slot['inizio']}-{slot['fine']})")
            
            for i_lab, laboratorio in enumerate(LABORATORI):
                colonna_corrente = [riga_l1, riga_l2, riga_l3][i_lab]
                chiave = (data_selezionata, laboratorio, slot['ora'])
                
                with colonna_corrente:
                    if not slot['prenotabile']:
                        st.button("☕ Intervallo", key=f"int_{laboratorio}_{slot['ora']}", disabled=True, use_container_width=True)
                    
                    elif chiave in st.session_state.manutenzioni:
                        # Se l'admin ci clicca, sblocca il laboratorio istantaneamente
                        st.button(
                            "🔧 GUASTO \n[Sblocca]", 
                            key=f"btn_{chiave}", 
                            type="secondary", 
                            use_container_width=True,
                            disabled=(ruolo != "Tecnico / Amministratore"),
                            on_click=gestisci_manutenzione,
                            args=(chiave, "disattiva")
                        )
                    
                    elif chiave in st.session_state.prenotazioni:
                        proprietario = st.session_state.prenotazioni[chiave]['prof']
                        motivo_pren = st.session_state.prenotazioni[chiave]['motivo']
                        
                        if proprietario == utente_attivo:
                            # Se clicchi sul TUO bottone rosso, si cancella subito
                            st.button(
                                f"📋 Tuo: {motivo_pren[:10]} \n[CANCELLA]", 
                                key=f"btn_{chiave}", 
                                type="secondary", 
                                use_container_width=True,
                                on_click=cancella_prenotazione,
                                args=(chiave,)
                            )
                        else:
                            # Se è di un altro professore, mostra chi lo occupa (pulsante disattivato per te)
                            st.button(f"🔴 {proprietario[:10]} \n({motivo_pren[:10]})", key=f"btn_{chiave}", type="secondary", use_container_width=True, disabled=True)
                    else:
                        # Se lo slot è LIBERO (Verde)
                        if ruolo == "Professore":
                            # Il professore prenota all'istante
                            st.button("🟢 LIBERO \n[Prenota]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=esegui_prenotazione, args=(chiave, utente_attivo))
                        elif ruolo == "Tecnico / Amministratore":
                            # L'admin mette in manutenzione all'istante
                            st.button("🟢 LIBERO \n[Disattiva Aula]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=gestisci_manutenzione, args=(chiave, "attiva"))
                        else:
                            # Gli studenti vedono solo la dicitura Libero senza poter cliccare
                            st.button("🟢 LIBERO", key=f"btn_{chiave}", type="primary", use_container_width=True, disabled=True)
            st.write("---")

        # ==========================================
        # STRUMENTO DI PERSONALIZZAZIONE TESTI
        # ==========================================
        if ruolo == "Professore":
            st.write("### 📝 Personalizza il nome della tua lezione")
            mie_p = [k for k, v in st.session_state.prenotazioni.items() if v["prof"] == utente_attivo and k[0] == data_selezionata]
            
            if mie_p:
                scelta_p = st.selectbox("Seleziona quale delle tue ore odierne vuoi modificare:", mie_p, format_func=lambda x: f"{x[1]} alla {x[2]}")
                nuovo_motivo = st.text_input("Inserisci Classe e Materia (Es: 4A - AutoCAD):", value=st.session_state.prenotazioni[scelta_p]["motivo"])
                if st.button("Salva ed esponi sul tabellone", type="primary"):
                    st.session_state.prenotazioni[scelta_p]["motivo"] = nuovo_motivo
                    st.rerun()
            else:
                st.info("💡 Fai clic su un pulsante verde `🟢 LIBERO` del tabellone in alto per creare all'istante la tua prima prenotazione di oggi.")
