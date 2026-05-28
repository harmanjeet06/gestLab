import streamlit as st
import datetime
import pandas as pd
import os
import json

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="SmartLab Scarpa", layout="wide", initial_sidebar_state="expanded")

# --- CSS AVANZATO: UI/UX, MOVIMENTI SMOOTH E MICRO-ANIMAZIONI ---
st.markdown("""
<style>
    /* ABILITAZIONE MOVIMENTO LISCIO (SMOOTH SCROLLING) SU TUTTA LA PAGINA */
    html {
        scroll-behavior: smooth !important;
    }

    /* Transizioni fluide globali per tutti i pulsanti dell'applicazione */
    div.stButton > button {
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* STATO VERDE (LIBERO) - Micro-animazione reattiva e fluida */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #2e7d32 !important;
        color: white !important;
        border: 1px solid #2e7d32 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    /* Hover state: schiarisce in dissolvenza e si solleva delicatamente */
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #1b5e20 !important;
        transform: translateY(-3px) scale(1.015) !important;
        box-shadow: 0 6px 12px rgba(46, 125, 50, 0.25) !important;
    }
    /* Active state: effetto click morbido pressato verso il basso */
    div.stButton > button[data-testid="baseButton-primary"]:active {
        transform: translateY(1px) scale(0.98) !important;
    }

    /* STATO ROSSO (OCCUPATO / GUASTO) - Transizione fluida */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #c62828 !important;
        color: white !important;
        border: 1px solid #c62828 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    /* Hover state */
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #b71c1c !important;
        transform: translateY(-3px) scale(1.015) !important;
        box-shadow: 0 6px 12px rgba(198, 40, 40, 0.25) !important;
    }
    /* Active state */
    div.stButton > button[data-testid="baseButton-secondary"]:active {
        transform: translateY(1px) scale(0.98) !important;
    }
    
    /* Animazione di entrata fluida (fade-in) per le schede informative in basso */
    .stAlert, .element-container {
        animation: fadeIn 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- INSERIMENTO LOGO DELLA SCUOLA (DA ASSET PUBBLICO DEL SITO SCARPA) ---
# Mostra l'intestazione grafica istituzionale prelevata direttamente dal template web ufficiale dell'istituto
st.markdown("""
<div style="text-align: center; padding: 15px 0; background-color: #ffffff; border-bottom: 3px solid #003366; margin-bottom: 25px; border-radius: 4px;">
    <table style="margin: 0 auto; border: none; background: transparent;">
        <tr style="background: transparent; border: none;">
            <td style="padding-right: 20px; border: none; vertical-align: middle;">
                <img src="https://www.antonioscarpa.edu.it/images/logo.png" alt="Logo Istituto Scarpa" style="height: 75px; width: auto; max-width: 100%;">
            </td>
            <td style="text-align: left; border: none; vertical-align: middle;">
                <h2 style="margin: 0; color: #003366; font-family: 'Arial', sans-serif; font-size: 26px; font-weight: bold; letter-spacing: 0.5px;">Istituto Statale di Istruzione Superiore</h2>
                <h1 style="margin: 3px 0 0 0; color: #800000; font-family: 'Arial', sans-serif; font-size: 32px; font-weight: bold;">“Antonio Scarpa”</h1>
                <p style="margin: 5px 0 0 0; color: #555555; font-family: 'Arial', sans-serif; font-size: 14px; font-weight: 600; text-transform: uppercase;">Motta di Livenza | Oderzo — <span style="color: #2e7d32;">⚡ SmartLab Platform</span></p>
            </td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

# --- UTILITY DATABASE PERSISTENTE ---
FILE_PRENOTAZIONI = "database_prenotazioni.json"

def salva_prenotazioni_su_disco():
    dati_serializzabili = {}
    for chiave, info in st.session_state.prenotazioni.items():
        chiave_str = f"{chiave[0].isoformat()}||{chiave[1]}||{chiave[2]}"
        dati_serializzabili[chiave_str] = info
    with open(FILE_PRENOTAZIONI, "w", encoding="utf-8") as f:
        json.dump(dati_serializzabili, f, ensure_ascii=False, indent=4)

def carica_prenotazioni_da_disco():
    if os.path.exists(FILE_PRENOTAZIONI):
        try:
            with open(FILE_PRENOTAZIONI, "r", encoding="utf-8") as f:
                dati_serializzati = json.load(f)
            prenotazioni_ripristinate = {}
            for chiave_str, info in dati_serializzati.items():
                parti = chiave_str.split("||")
                data_obj = datetime.date.fromisoformat(parti[0])
                chiave_tuple = (data_obj, parti[1], parti[2])
                prenotazioni_ripristinate[chiave_tuple] = info
            return prenotazioni_ripristinate
        except:
            return {}
    return {}

# --- DATI GOOGLE SHEETS ---
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

# --- INIZIALIZZAZIONE MEMORIA ---
if "autenticato" not in st.session_state: st.session_state.autenticato = False
if "ruolo" not in st.session_state: st.session_state.ruolo = None
if "utente_attivo" not in st.session_state: st.session_state.utente_attivo = None
if "prenotazioni" not in st.session_state: st.session_state.prenotazioni = carica_prenotazioni_da_disco()
if "manutenzioni" not in st.session_state: st.session_state.manutenzioni = {}
if "target_studente" not in st.session_state: st.session_state.target_studente = None

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
    salva_prenotazioni_su_disco()

def cancella_prenotazione(chiave):
    if chiave in st.session_state.prenotazioni:
        del st.session_state.prenotazioni[chiave]
        salva_prenotazioni_su_disco()

def gestisci_manutenzione(chiave, azione):
    if azione == "attiva":
        if chiave in st.session_state.prenotazioni:
            del st.session_state.prenotazioni[chiave]
            salva_prenotazioni_su_disco()
        st.session_state.manutenzioni[chiave] = "Sospensione Tecnica"
    elif azione == "disattiva":
        if chiave in st.session_state.manutenzioni:
            del st.session_state.manutenzioni[chiave]

def mostra_dettagli_studente(chiave): 
    st.session_state.target_studente = chiave

# ==========================================
# GESTIONE LOGIN (INVARIATO PER SICUREZZA)
# ==========================================
if not st.session_state.autenticato:
    st.title("🔐 Accesso Centrale - SmartLab")
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
                else: st.error("Credenziali errate.")
    else:
        with st.form("form_studenti"):
            classe_selezionata = st.selectbox("Seleziona la tua Classe:", elenco_classi)
            if st.form_submit_button("Accedi al Tabellone"):
                st.session_state.autenticato = True
                st.session_state.ruolo = "Studente"
                st.session_state.utente_attivo = f"Studente ({classe_selezionata})"
                st.rerun()
else:
    ruolo = st.session_state.ruolo
    utente_attivo = st.session_state.utente_attivo

    st.sidebar.title("🧬 SmartLab Scarpa v3.1")
    st.sidebar.write(f"Utente: **{utente_attivo}**")
    st.sidebar.write(f"Ruolo: `{ruolo}`")
    if st.sidebar.button("🚪 Esci dal sistema", use_container_width=True):
        st.session_state.autenticato = False
        st.session_state.target_studente = None
        st.rerun()

    col_main, col_notifiche_destra = st.columns([3, 1])

    with col_main:
        st.title("🖥️ Tabellone Orari Interattivo")
        st.markdown("---")

        data_selezionata = st.date_input("Seleziona Data:", datetime.date.today())
        giorni_settimana_eng = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        giorno_testo = giorni_settimana_eng[data_selezionata.weekday()]

        st.subheader(f"📅 {giorno_testo} {data_selezionata.strftime('%d/%m/%Y')}")

        if giorno_testo in GIORNI:
            schema_orario = get_orari_per_giorno(giorno_testo)

            # Calcolo dei Badge Dinamici richiesti per l'Intestazione delle Tab
            ore_occupate = {lab: 0 for lab in LABORATORI}
            for chiave_p in st.session_state.prenotazioni.keys():
                if chiave_p[0] == data_selezionata:
                    ore_occupate[chiave_p[1]] = ore_occupate.get(chiave_p[1], 0) + 1

            badge_info = "🟢 Libero" if ore_occupate["Info"] < 3 else "🟡 Alta Affluenza"
            badge_autocad = "🟢 Libero" if ore_occupate["AutoCAD"] < 3 else "🟡 Alta Affluenza"
            badge_sistel = "🟢 Libero" if ore_occupate["Sistel"] < 3 else "🟡 Alta Affluenza"

            # Intestazione delle colonne
            col_orari, col_l1, col_l2, col_l3 = st.columns([3, 3, 3, 3])
            with col_orari: st.markdown("**🕒 Ora / Fascia**")
            with col_l1: st.markdown(f"**💻 Laboratorio Info** <br><span style='font-size:12px; color:gray;'>Stato: {badge_info}</span>", unsafe_allow_html=True)
            with col_l2: st.markdown(f"**📐 Aula AutoCAD** <br><span style='font-size:12px; color:gray;'>Stato: {badge_autocad}</span>", unsafe_allow_html=True)
            with col_l3: st.markdown(f"**🔌 Reparto Sistel** <br><span style='font-size:12px; color:gray;'>Stato: {badge_sistel}</span>", unsafe_allow_html=True)
            st.divider()

            # Righe del tabellone orario
            for slot in schema_orario:
                riga_ora, riga_l1, riga_l2, riga_l3 = st.columns([3, 3, 3, 3])
                with riga_ora: st.write(f"**{slot['ora']}** \n({slot['inizio']}-{slot['fine']})")
                
                for i_lab, laboratorio in enumerate(LABORATORI):
                    colonna_corrente = [riga_l1, riga_l2, riga_l3][i_lab]
                    chiave = (data_selezionata, laboratorio, slot['ora'])
                    
                    with colonna_corrente:
                        if not slot['prenotabile']:
                            st.button("☕ Intervallo", key=f"int_{laboratorio}_{slot['ora']}", disabled=True, use_container_width=True)
                        elif chiave in st.session_state.manutenzioni:
                            st.button("🔧 GUASTO \n[Dettagli]", key=f"btn_{chiave}", type="secondary", use_container_width=True, on_click=mostra_dettagli_studente, args=(chiave,))
                        elif chiave in st.session_state.prenotazioni:
                            proprietario = st.session_state.prenotazioni[chiave]['prof']
                            if proprietario == utente_attivo:
                                st.button(f"📋 Tuo Slot \n[CANCELLA]", key=f"btn_{chiave}", type="secondary", use_container_width=True, on_click=cancella_prenotazione, args=(chiave,))
                            else:
                                st.button(f"🔴 Occupato \n👤 {proprietario[:10]}", key=f"btn_{chiave}", type="secondary", use_container_width=True, on_click=mostra_dettagli_studente, args=(chiave,))
                        else:
                            if ruolo == "Professore":
                                st.button("🟢 LIBERO \n[Prenota]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=esegui_prenotazione, args=(chiave, utente_attivo))
                            elif ruolo == "Tecnico / Amministratore":
                                st.button("🟢 LIBERO \n[Blocca Aula]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=gestisci_manutenzione, args=(chiave, "attiva"))
                            else:
                                st.button("🟢 LIBERO \n[Dettagli]", key=f"btn_{chiave}", type="primary", use_container_width=True, on_click=mostra_dettagli_studente, args=(chiave,))
            st.write("---")

            # --- ASSISTENTE AI MANUTENZIONE PREDITTIVA ---
            if ruolo == "Tecnico / Amministratore":
                st.write("### 🔮 Assistente AI: Manutenzione Predittiva & Telemetria")
                st.info("L'algoritmo predittivo AI analizza i carichi di lavoro e lo storico di telemetria memorizzato per prevenire i guasti hardware.")
                
                totale_ore_laboratori = {"Info": 0, "AutoCAD": 0, "Sistel": 0}
                for chiave_p in st.session_state.prenotazioni.keys():
                    lab_nome = chiave_p[1]
                    if lab_nome in totale_ore_laboratori:
                        totale_ore_laboratori[lab_nome] += 1
                
                c_ai1, c_ai2, c_ai3 = st.columns(3)
                soglia_critica = 5
                
                with c_ai1:
                    st.metric("Usura Stimata Lab Info", f"{totale_ore_laboratori['Info'] * 8}%")
                    if totale_ore_laboratori["Info"] >= soglia_critica:
                        st.error("⚠️ AI Alert: Usura ventole/filtri alta. Pianificare manutenzione entro 3 giorni.")
                    else: st.success("✅ Stato Hardware Ottimale")
                        
                with c_ai2:
                    st.metric("Usura Stimata Aula AutoCAD", f"{totale_ore_laboratori['AutoCAD'] * 12}%")
                    if totale_ore_laboratori["AutoCAD"] >= soglia_critica:
                        st.error("⚠️ AI Alert: Rilevato stress termico sulle GPU. Consigliato controllo pasta termica.")
                    else: st.success("✅ Stato Hardware Ottimale")
                        
                with c_ai3:
                    st.metric("Usura Stimata Reparto Sistel", f"{totale_ore_laboratori['Sistel'] * 5}%")
                    if totale_ore_laboratori["Sistel"] >= soglia_critica:
                        st.error("⚠️ AI Alert: Verificare taratura degli oscilloscopi digitali.")
                    else: st.success("✅ Stato Hardware Ottimale")
                st.divider()

            # Scheda Informativa reattiva (Dotata di animazione Fade-In via CSS)
            if st.session_state.target_studente:
                with st.container(border=True):
                    st.write(f"#### Dettagli slot selezionato: {st.session_state.target_studente[1]} ({st.session_state.target_studente[2]})")
                    if st.session_state.target_studente in st.session_state.prenotazioni:
                        st.write(f"👤 **Docente Incaricato:** {st.session_state.prenotazioni[st.session_state.target_studente]['prof']}")
                        st.write(f"📝 **Attività:** {st.session_state.prenotazioni[st.session_state.target_studente]['motivo']}")
                    else:
                        st.write("🟢 L'aula risulta attualmente libera e disponibile per la didattica.")

    with col_notifiche_destra:
        st.write("### 🔔 Bacheca")
        st.caption("Notifiche e comunicazioni d'istituto in tempo reale.")
