import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GestLab Cloud Secure", layout="wide", initial_sidebar_state="expanded")

# --- CONNESSIONE A GOOGLE SHEETS (VIA URL CSV PUBBLICO) ---
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

# --- INIZIALIZZAZIONE DELLA SESSIONE ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "ruolo" not in st.session_state:
    st.session_state.ruolo = None
if "utente_attivo" not in st.session_state:
    st.session_state.utente_attivo = None

if "prenotazioni" not in st.session_state:
    st.session_state.prenotazioni = {}
if "scambi" not in st.session_state:
    st.session_state.scambi = []
if "manutenzioni" not in st.session_state:
    st.session_state.manutenzioni = {}

if "lab_selezionato_click" not in st.session_state:
    st.session_state.lab_selezionato_click = "Info"
if "ora_selezionata_click" not in st.session_state:
    st.session_state.ora_selezionata_click = "1ª ora"

dizionario_utenti = carica_utenti_da_sheets()
elenco_classi = carica_classi_da_sheets()

# --- COSTRUTTORE STRUTTURA ORARI ---
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
    st.write("I dati di accesso sono verificati in tempo reale su Google Sheets Database.")
    
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
                    st.success("Accesso Amministratore sbloccato!")
                    st.rerun()
                elif user_clean in dizionario_utenti and dizionario_utenti[user_clean]["password"] == pass_clean:
                    st.session_state.autenticato = True
                    st.session_state.ruolo = dizionario_utenti[user_clean]["ruolo"]
                    st.session_state.utente_attivo = dizionario_utenti[user_clean]["nominativo"]
                    st.success("Autenticato!")
                    st.rerun()
                else:
                    st.error("Credenziali non corrette.")
                    
    else:  # Studente
        with st.form("form_studenti"):
            classe_selezionata = st.selectbox("Seleziona la tua Classe:", elenco_classi)
            pulsante_studente = st.form_submit_button("Accedi al Tabellone")
            
            if pulsante_studente:
                st.session_state.autenticato = True
                st.session_state.ruolo = "Studente"
                st.session_state.utente_attivo = f"Studente ({classe_selezionata})"
                st.success("Benvenuto!")
                st.rerun()

# ==========================================
# APPLICAZIONE ATTIVA (TABELLONE ALLINEATO)
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
        
    st.sidebar.divider()
    if st.sidebar.button("🔄 Forza Aggiornamento Database"):
        st.cache_data.clear()
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

    if giorno_testo in GIORNI:
        schema_orario = get_orari_per_giorno(giorno_testo)

        st.write("### 📊 Stato Disponibilità")
        
        # DEFINIZIONE INTESTAZIONI GRIGLIA
        col_orari, col_l1, col_l2, col_l3 = st.columns([3, 3, 3, 3])
        with col_orari: st.markdown("**🕒 Ora / Fascia**")
        with col_l1: st.markdown("**💻 Laboratorio Info**")
        with col_l2: st.markdown("**📐 Laboratorio AutoCAD**")
        with col_l3: st.markdown("**🔌 Laboratorio Sistel**")
        st.divider()

        # COSTRUZIONE RIGIDA RIGA PER RIGA (Previene qualsiasi scombinazione grafica)
        for slot in schema_orario:
            riga_ora, riga_l1, riga_l2, riga_l3 = st.columns([3, 3, 3, 3])
            
            # 1. Colonna Orario
            with riga_ora:
                st.write(f"**{slot['ora']}** \n({slot['inizio']} - {slot['fine']})")
            
            # Ciclo sui 3 laboratori per la riga corrente
            for i_lab, laboratorio in enumerate(LABORATORI):
                colonna_corrente = [riga_l1, riga_l2, riga_l3][i_lab]
                chiave = (data_selezionata, laboratorio, slot['ora'])
                
                with colonna_corrente:
                    if not slot['prenotabile']:
                        st.button("☕ Intervallo", key=f"int_{laboratorio}_{slot['ora']}", disabled=True, use_container_width=True)
                    
                    elif chiave in st.session_state.manutenzioni:
                        st.button(f"🔧 GUASTO: {st.session_state.manutenzioni[chiave][:15]}...", key=f"btn_{chiave}", disabled=True, use_container_width=True)
                    
                    elif chiave in st.session_state.prenotazioni:
                        proprietario = st.session_state.prenotazioni[chiave]['prof']
                        motivo_pren = st.session_state.prenotazioni[chiave]['motivo']
                        
                        if proprietario == utente_attivo:
                            if st.button(f"📋 Tuo ({motivo_pren[:12]})", key=f"btn_{chiave}", type="secondary", use_container_width=True):
                                st.toast("Usa il pannello in basso per cancellare.")
                        else:
                            if st.button(f"🔴 {proprietario[:12]} ({motivo_pren[:10]})", key=f"btn_{chiave}", type="secondary", use_container_width=True):
                                if ruolo == "Professore":
                                    st.session_state.lab_selezionato_click = laboratorio
                                    st.session_state.ora_selezionata_click = slot['ora']
                                    st.toast(f"Selezionato slot di {proprietario} per scambio.")
                                    st.rerun()
                    else:
                        # Spieghiamo a Streamlit che LIBERO = Tasto Principale (Verde nativo nei temi dark/light corretti)
                        if st.button("🟢 LIBERO (Seleziona)", key=f"btn_{chiave}", type="primary", use_container_width=True):
                            if ruolo in ["Professore", "Tecnico / Amministratore"]:
                                st.session_state.lab_selezionato_click = laboratorio
                                st.session_state.ora_selezionata_click = slot['ora']
                                st.toast(f"Selezionato: {laboratorio} - {slot['ora']}")
                                st.rerun()
            st.write("---") # Sottile linea di allineamento orizzontale tra le ore

        # ==========================================
        # AREA OPERATIVA SOTTOSTANTE
        # ==========================================
        st.write("### ⚙️ Area Operativa")
        st.success(f"📍 Slot selezionato dal tabellone: **{st.session_state.lab_selezionato_click}** alla **{st.session_state.ora_selezionata_click}**")

        if ruolo == "Professore":
            tab1, tab2, tab3 = st.tabs(["🆕 Nuova Prenotazione", "🔄 Richiedi Scambio", "📋 Mie Prenotazioni"])
            
            with tab1:
                st.subheader("Blocca lo slot selezionato")
                lab_scelto = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click), key="sel_l")
                ore_disp = [s['ora'] for s in schema_orario if s['prenotabile']]
                ora_scelta = st.selectbox("Ora:", ore_disp, index=ore_disp.index(st.session_state.ora_selezionata_click), key="sel_o")
                motivo = st.text_input("Attività didattica (Classe / Materia):", key="act")
                
                if st.button("Conferma e Salva", type="primary", key="save_p"):
                    chiave_pren = (data_selezionata, lab_scelto, ora_scelta)
                    if chiave_pren in st.session_state.prenotazioni:
                        st.error("Slot già occupato.")
                    elif motivo.strip() == "":
                        st.warning("Inserisci la materia.")
                    else:
                        st.session_state.prenotazioni[chiave_pren] = {"prof": utente_attivo, "motivo": motivo}
                        st.success("Prenotazione salvata!")
                        st.rerun()

            with tab2:
                st.subheader("Invia proposta di scambio")
                lab_scambio = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click), key="s_l")
                ora_scambio = st.selectbox("Ora:", [s['ora'] for s in schema_orario if s['prenotabile']], index=[s['ora'] for s in schema_orario if s['prenotabile']].index(st.session_state.ora_selezionata_click), key="s_o")
                chiave_scambio = (data_selezionata, lab_scambio, ora_scambio)
                
                if chiave_scambio in st.session_state.prenotazioni:
                    prof_dest = st.session_state.prenotazioni[chiave_scambio]['prof']
                    if prof_dest != utente_attivo:
                        st.write(f"Stai chiedendo lo scambio a: **{prof_dest}**")
                        msg = st.text_area("Messaggio per il collega:")
                        if st.button("Spedisci richiesta", key="send_s"):
                            st.session_state.scambi.append({"da_prof": utente_attivo, "a_prof": prof_dest, "data": data_selezionata, "lab": lab_scambio, "ora": ora_scambio, "messaggio": msg, "stato": "In attesa"})
                            st.success("Richiesta inviata!")
                else:
                    st.info("Lo slot è vuoto, puoi bloccarlo direttamente nel primo tab.")

            with tab3:
                st.subheader("Riepilogo ore prenotate a tuo nome")
                elenco_mie = [k for k, v in st.session_state.prenotazioni.items() if v["prof"] == utente_attivo]
                if not elenco_mie:
                    st.write("Non hai prenotazioni attive per oggi.")
                for k in elenco_mie:
                    st.write(f"• **{k[1]}** alla **{k[2]}** -> *{st.session_state.prenotazioni[k]['motivo']}*")
                    if st.button("Elimina", key=f"del_{k[1]}_{k[2]}"):
                        del st.session_state.prenotazioni[k]
                        st.rerun()

        elif ruolo == "Studente":
            st.subheader("🔍 Ricerca rapida lezioni")
            testo_cercato = st.text_input("Inserisci classe o materia:")
            if testo_cercato:
                trovato = False
                for k, v in st.session_state.prenotazioni.items():
                    if testo_cercato.lower() in v["motivo"].lower() and k[0] == data_selezionata:
                        st.write(f"📖 **{k[1]}** | Ora: **{k[2]}** -> Classe: {v['motivo']} (Docente: {v['prof']})")
                        trovato = True
                if not trovato:
                    st.write("Nessuna corrispondenza trovata.")

        elif ruolo == "Tecnico / Amministratore":
            st.subheader("🔧 Pannello Manutenzioni Hardware")
            lab_m = st.selectbox("Laboratorio:", LABORATORI, index=LABORATORI.index(st.session_state.lab_selezionato_click))
            ora_m = st.selectbox("Ora:", [s['ora'] for s in schema_orario if s['prenotabile']], index=[s['ora'] for s in schema_orario if s['prenotabile']].index(st.session_state.ora_selezionata_click))
            motivo_m = st.text_input("Guasto riscontrato:")
            
            if st.button("Metti in Manutenzione", type="primary"):
                if motivo_m.strip():
                    chiave_m = (data_selezionata, lab_m, ora_m)
                    if chiave_m in st.session_state.prenotazioni:
                        del st.session_state.prenotazioni[chiave_m]
                    st.session_state.manutenzioni[chiave_m] = motivo_m
                    st.success("Sospensione applicata!")
                    st.rerun()
