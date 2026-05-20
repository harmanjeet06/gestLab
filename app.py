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
if "scambi" not in st.session_state: st.session_state.scambi = []

# Supporto per mirare lo scambio cliccando sul tabellone
if "target_scambio" not in st.session_state: st.session_state.target_scambio = None

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

# --- FUNZIONI DI CALLBACK ---
def esegui_prenotazione(chiave, prof):
    st.session_state.prenotazioni[chiave] = {"prof": prof, "motivo": "Lezione Didattica"}

def cancella_prenotazione(chiave):
    if chiave in st.session_state.prenotazioni:
        del st.session_state.prenotazioni[chiave]

def prepara_scambio(chiave):
    st.session_state.target_scambio = chiave

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
# APPLICAZIONE ATTIVA
# ==========================================
else:
    ruolo = st.session_state.ruolo
    utente_attivo = st.session_state.utente_attivo

    # Barra laterale classica (Sinistra) solo per Info Utente e Uscita
    st.sidebar.title("🧬 GestLab v1.8")
    st.sidebar.write(f"Utente: **{utente_attivo}**")
    st.sidebar.write(f"Ruolo: `{ruolo}`")
    if st.sidebar.button("🚪 Esci"):
        st.session_state.autenticato = False
        st.rerun()
    if st.sidebar.button("🔄 Aggiorna DB"):
        st.cache_data.clear()
        st.rerun()

    # LAYOUT PRINCIPALE STRUTTURATO A DUE COLONNE (Tabellone a sinistra, Notifiche a destra)
    col_main, col_notifiche_destra = st.columns([3, 1])

    with col_main:
        st.title("🖥️ Tabellone Orari Interattivo")
        st.write("👉 Clicca su `🟢 LIBERO` per prenotare o sul tuo bottone rosso per cancellare. Clicca sul tasto rosso di un **collega** per proporgli uno scambio.")
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
                                st.button(
                                    f"📋 Tuo: {motivo_pren[:10]} \n[CANCELLA]", 
                                    key=f"btn_{chiave}", 
                                    type="secondary", 
                                    use_container_width=True,
                                    on_click=cancella_prenotazione,
                                    args=(chiave,)
                                )
                            else:
                                st.button(
                                    f"🔴 {proprietario[:10]} \n({motivo_pren[:10]})", 
                                    key=f"btn_{chiave}", 
                                    type="secondary", 
                                    use_container_width=True,
                                    on_click=prepara_scambio,
                                    args=(chiave,)
                                )
                        else:
                            if ruolo == "Professore":
                                st.button("🟢 LIBERO \n[Prenota]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=esegui_prenotazione, args=(chiave, utente_attivo))
                            elif ruolo == "Tecnico / Amministratore":
                                st.button("🟢 LIBERO \n[Blocca Aula]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=gestisci_manutenzione, args=(chiave, "attiva"))
                            else:
                                st.button("🟢 LIBERO", key=f"btn_{chiave}", type="primary", use_container_width=True, disabled=True)
                st.write("---")

            # ==========================================
            # PANNELLO STRUMENTI IN BASSO
            # ==========================================
            if ruolo == "Professore":
                st.write("### ⚙️ Centro Operativo")
                tab_desc, tab_scambio, tab_storico = st.tabs(["📝 Descrizione Ore", "🔄 Proponi Scambio d'Aula", "📋 Storico Richieste Inviate"])
                
                with tab_desc:
                    mie_p = [k for k, v in st.session_state.prenotazioni.items() if v["prof"] == utente_attivo and k[0] == data_selezionata]
                    if mie_p:
                        scelta_p = st.selectbox("Personalizza la descrizione di una tua ora di oggi:", mie_p, format_func=lambda x: f"{x[1]} alla {x[2]}")
                        nuovo_motivo = st.text_input("Classe e Materia:", value=st.session_state.prenotazioni[scelta_p]["motivo"])
                        if st.button("Aggiorna sul Tabellone"):
                            st.session_state.prenotazioni[scelta_p]["motivo"] = nuovo_motivo
                            st.success("Tabellone aggiornato!")
                            st.rerun()
                    else:
                        st.info("💡 Non hai ancora ore prenotate oggi sul tabellone.")

                with tab_scambio:
                    if st.session_state.target_scambio:
                        t_data, t_lab, t_ora = st.session_state.target_scambio
                        if st.session_state.target_scambio in st.session_state.prenotazioni:
                            collega_proprietario = st.session_state.prenotazioni[st.session_state.target_scambio]["prof"]
                            
                            st.warning(f"Stai chiedendo lo scambio per lo slot: **{t_lab}** alla **{t_ora}** di **{collega_proprietario}**")
                            nota_scambio = st.text_area("Scrivi un messaggio per il collega:")
                            
                            col_scambio1, col_scambio2 = st.columns(2)
                            with col_scambio1:
                                if st.button("Invia Proposta di Scambio", type="primary"):
                                    # [RISOLTO BUG KEYERROR]: Aggiunto il campo "data" all'interno del dizionario scambi
                                    st.session_state.scambi.append({
                                        "da": utente_attivo,
                                        "a": collega_proprietario,
                                        "data": t_data,
                                        "lab": t_lab,
                                        "ora": t_ora,
                                        "nota": nota_scambio,
                                        "stato": "In attesa"
                                    })
                                    st.success(f"Richiesta inviata! Il collega la vedrà nel suo Centro Notifiche a destra.")
                                    st.session_state.target_scambio = None
                                    st.rerun()
                            with col_scambio2:
                                if st.button("Annulla"):
                                    st.session_state.target_scambio = None
                                    st.rerun()
                        else:
                            st.session_state.target_scambio = None
                    else:
                        st.info("👉 Fai clic sul pulsante rosso di un collega sul tabellone in alto per avviare una richiesta di scambio.")

                with tab_storico:
                    mie_richieste = [s for s in st.session_state.scambi if s["da"] == utente_attivo]
                    st.write("#### 📤 Stato delle richieste che hai inviato ai colleghi")
                    if not mie_richieste:
                        st.write("*Non hai inviato nessuna richiesta.*")
                    for r in mie_richieste:
                        colore_stato = "🟡" if "In attesa" in r["stato"] else ("🟢" if "Accettato" in r["stato"] else "🔴")
                        st.write(f"{colore_stato} Per **{r['lab']}** ({r['ora']}) del {r['data'].strftime('%d/%m')} inviata a **{r['a']}** $\rightarrow$ Stato: **{r['stato']}**")

            elif ruolo == "Studente":
                st.write("### 🔍 Cerca la tua lezione")
                testo = st.text_input("Inserisci classe o materia:")
                if testo:
                    for k, v in st.session_state.prenotazioni.items():
                        if testo.lower() in v["motivo"].lower() and k[0] == data_selezionata:
                            st.write(f"📖 **{k[1]}** | Ora: **{k[2]}** -> Docente: {v['prof']} ({v['motivo']})")

    # --------------------------------------------------
    # COLONNA DI DESTRA: CENTRO NOTIFICHE INTERATTIVO
    # --------------------------------------------------
    with col_notifiche_destra:
        st.write("### 🔔 Centro Notifiche")
        st.write("Gestisci qui le richieste dei colleghi.")
        st.divider()
        
        if ruolo == "Professore":
            richieste_ricevute = [idx for idx, s in enumerate(st.session_state.scambi) if s["a"] == utente_attivo and s["stato"] == "In attesa"]
            
            if not richieste_ricevute:
                st.info("🟢 Nessuna richiesta in sospeso.")
            else:
                for idx in richieste_ricevute:
                    req = st.session_state.scambi[idx]
                    with st.expander(f"📥 Da: {req['da']}", expanded=True):
                        st.write(f"**Aula:** {req['lab']}")
                        st.write(f"**Ora:** {req['ora']}")
                        st.write(f"**Giorno:** {req['data'].strftime('%d/%m/%Y')}")
                        st.write(f"*Messaggio:* {req['nota']}")
                        st.write("---")
                        
                        # Tasto per Accettare lo scambio
                        if st.button("✅ Accetta", key=f"acc_{idx}", use_container_width=True):
                            chiave_target = (req['data'], req['lab'], req['ora'])
                            # Scambio effettivo sul tabellone
                            st.session_state.prenotazioni[chiave_target] = {"prof": req['da'], "motivo": "Scambio Concesso"}
                            st.session_state.scambi[idx]["stato"] = "Accettato"
                            st.toast("Scambio approvato!")
                            st.rerun()
                        
                        # Sezione Rifiuto con Motivazione
                        motivo_rifiuto = st.text_input("Motivo del rifiuto:", key=f"mot_{idx}", placeholder="Es: Devo fare una verifica...")
                        if st.button("❌ Rifiuta", key=f"rif_{idx}", use_container_width=True):
                            if motivo_rifiuto.strip() == "":
                                st.error("Inserisci una motivazione prima di rifiutare!")
                            else:
                                st.session_state.scambi[idx]["stato"] = f"Rifiutato: {motivo_rifiuto}"
                                st.toast("Scambio rifiutato con motivazione.")
                                st.rerun()
        else:
            st.caption("Le notifiche di scambio sono disponibili solo per gli account Docente.")
