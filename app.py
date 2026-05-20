import streamlit as st
import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GestLab - Prenotazione Laboratori", layout="wide", initial_sidebar_state="expanded")

# --- INIZIALIZZAZIONE DELLO STATO (DATABASE IN MEMORIA) ---
if "prenotazioni" not in st.session_state:
    # Struttura: {(data, laboratorio, slot): {"prof": Nome, "motivo": Motivo, "stato": Stato}}
    st.session_state.prenotazioni = {}

if "scambi" not in st.session_state:
    # Lista di richieste di scambio
    st.session_state.scambi = []

if "manutenzioni" not in st.session_state:
    # Struttura: {(data, laboratorio, slot): Motivo_Manutenzione}
    st.session_state.manutenzioni = {}

# --- FUNZIONI DI UTILITÀ ORARI ---
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]
LABORATORI = ["Sistel Info", "AutoCAD"]

def get_orari_per_giorno(giorno):
    """Restituisce lo schema orario in base al giorno della settimana"""
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
    else:  # Lunedì, Mercoledì, Giovedì
        return [
            {"ora": "1ª ora", "inizio": "08:00", "fine": "09:00", "prenotabile": True},
            {"ora": "2ª ora", "inizio": "09:00", "fine": "10:00", "prenotabile": True},
            {"ora": "3ª ora", "inizio": "10:00", "fine": "10:55", "prenotabile": True},
            {"ora": "Intervallo", "inizio": "10:55", "fine": "11:10", "prenotabile": False},
            {"ora": "4ª ora", "inizio": "11:10", "fine": "12:10", "prenotabile": True},
            {"ora": "5ª ora", "inizio": "12:10", "fine": "13:10", "prenotabile": True},
        ]

# --- BARRA LATERALE: AUTENTICAZIONE SIMULATA ---
st.sidebar.title("🧬 GestLab v1.0")
st.sidebar.write("Progetto Scolastico 2024/2025")
st.sidebar.hr()

st.sidebar.subheader("🔑 Autenticazione")
ruolo = st.sidebar.selectbox("Scegli il tuo Ruolo:", ["Professore", "Studente", "Tecnico / Amministratore"])

# Simulazione utente specifico in base al ruolo
if ruolo == "Professore":
    utente_attivo = st.sidebar.selectbox("Seleziona il tuo Nome:", ["Prof. Rossi", "Prof.ssa Bianchi", "Prof. Verdi"])
elif ruolo == "Studente":
    classe_studente = st.sidebar.selectbox("Seleziona la tua Classe:", ["5A INFO", "4B CAT", "3A INFO"])
    utente_attivo = f"Studente ({classe_studente})"
else:
    utente_attivo = "Tecnico Nicola"

st.sidebar.success(f"Loggato come: **{utente_attivo}**")

# --- TITOLO PRINCIPALE ---
st.title("🖥️ Sistema Gestione Laboratori Scolastici")
st.write(f"Benvenuto nel pannello di controllo. Ruolo attuale: **{ruolo}**")
st.hr()

# --- SELEZIONE DATA E GIORNO ---
col_data1, col_data2 = st.columns([1, 3])
with col_data1:
    data_selezionata = st.date_input("Seleziona una Data:", datetime.date.today())
    # Calcola il giorno della settimana in italiano
    giorni_settimana_eng = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    giorno_testo = giorni_settimana_eng[data_selezionata.weekday()]

with col_data2:
    st.subheader(f"📅 Vista Giornaliera: {giorno_testo} {data_selezionata.strftime('%d/%m/%Y')}")
    if giorno_testo in ["Sabato", "Domenica"]:
        st.warning("I laboratori sono chiusi durante il fine settimana. Seleziona un giorno da Lunedì a Venerdì.")

# Procediamo solo se è un giorno feriale scolastico
if giorno_testo in GIORNI:
    schema_orario = get_orari_per_giorno(giorno_testo)

    # --- TABELLA RIASSUNTIVA STATO LABORATORI ---
    st.write("### 📊 Stato Attuale dei Laboratori")
    
    # Prepariamo le colonne della tabella visiva
    col_orari, col_lab1, col_lab2 = st.columns([2, 4, 4])
    
    with col_orari:
        st.write("**Ora / Fascia**")
        for slot in schema_orario:
            st.write(f"🕒 **{slot['ora']}** ({slot['inizio']} - {slot['fine']})")
            
    # Gestione Lab 1: Sistel Info
    with col_lab1:
        st.write(f"🟩 **{LABORATORI[0]}** (Informatica)")
        for slot in schema_orario:
            chiave = (data_selezionata, LABORATORI[0], slot['ora'])
            
            if not slot['prenotabile']:
                st.info("☕ Intervallo (Chiuso)")
            elif chiave in st.session_state.manutenzioni:
                st.error(f"🔧 MANUTENZIONE: {st.session_state.manutenzioni[chiave]}")
            elif chiave in st.session_state.prenotazioni:
                pren = st.session_state.prenotazioni[chiave]
                st.warning(f"🔴 Occupato da {pren['prof']} ({pren['motivo']})")
            else:
                st.success("🟢 Libero")

    # Gestione Lab 2: AutoCAD
    with col_lab2:
        st.write(f"📐 **{LABORATORI[1]}** (Disegno Tecnico)")
        for slot in schema_orario:
            chiave = (data_selezionata, LABORATORI[1], slot['ora'])
            
            if not slot['prenotabile']:
                st.info("☕ Intervallo (Chiuso)")
            elif chiave in st.session_state.manutenzioni:
                st.error(f"🔧 MANUTENZIONE: {st.session_state.manutenzioni[chiave]}")
            elif chiave in st.session_state.prenotazioni:
                pren = st.session_state.prenotazioni[chiave]
                st.warning(f"🔴 Occupato da {pren['prof']} ({pren['motivo']})")
            else:
                st.success("🟢 Libero")

    st.hr()

    # ==========================================
    # INTERFACCIA 1: PROFESSORE
    # ==========================================
    if ruolo == "Professore":
        tab1, tab2, tab3 = st.tabs(["🆕 Nuova Prenotazione", "🔄 Gestione Scambi", "📋 Le Mie Prenotazioni"])
        
        with tab1:
            st.subheader("Effettua una prenotazione")
            lab_scelto = st.selectbox("Seleziona Laboratorio:", LABORATORI, key="prof_lab")
            
            # Filtra solo le ore effettivamente prenotabili e non in manutenzione
            ore_disponibili = [slot['ora'] for slot in schema_orario if slot['prenotabile']]
            ora_scelta = st.selectbox("Seleziona Ora:", ore_disponibili, key="prof_ora")
            motivo = st.text_input("Materia / Attività Didattica:", placeholder="Es. Laboratorio di Sistemi - Classe 5A")
            
            if st.button("Conferma Prenotazione", type="primary"):
                chiave_pren = (data_selezionata, lab_scelto, ora_scelta)
                
                if chiave_pren in st.session_state.manutenzioni:
                    st.error("Impossibile prenotare: Il laboratorio è sospeso per manutenzione ordinaria/straordinaria.")
                elif chiave_pren in st.session_state.prenotazioni:
                    prof_occupante = st.session_state.prenotazioni[chiave_pren]['prof']
                    st.error(f"Slot già occupato da {prof_occupante}. Puoi richiedere uno scambio nella scheda 'Gestione Scambi'.")
                elif motivo.strip() == "":
                    st.warning("Inserisci una motivazione o la materia per procedere.")
                else:
                    # Registra la prenotazione
                    st.session_state.prenotazioni[chiave_pren] = {
                        "prof": utente_attivo,
                        "motivo": motivo,
                        "stato": "Confermata"
                    }
                    st.success(f"Prenotazione effettuata con successo per {lab_scelto} alla {ora_scelta}!")
                    # Simulazione invio email a tutti i professori
                    st.info(f"📨 **NOTIFICA EMAIL INVIATA A TUTTI I PROFESSORI:** Il {utente_attivo} ha prenotato il laboratorio '{lab_scelto}' il giorno {data_selezionata.strftime('%d/%m/%Y')} alla {ora_scelta}.")
                    st.rerun()

        with tab2:
            st.subheader("Richiedi uno Scambio d'Orario")
            st.write("Se uno slot è occupato, puoi inviare una richiesta formale di scambio al collega.")
            
            lab_scambio = st.selectbox("Laboratorio dello scambio:", LABORATORI, key="scambio_lab")
            ora_scambio = st.selectbox("Ora dello scambio:", [slot['ora'] for slot in schema_orario if slot['prenotabile']], key="scambio_ora")
            
            chiave_scambio = (data_selezionata, lab_scambio, ora_scambio)
            
            if chiave_scambio in st.session_state.prenotazioni:
                prof_destinatario = st.session_state.prenotazioni[chiave_scambio]['prof']
                if prof_destinatario == utente_attivo:
                    st.info("Questo slot è già tuo!")
                else:
                    st.write(f"Lo slot attuale è occupato da: **{prof_destinatario}**")
                    messaggio_scambio = st.text_area("Messaggio per il collega:", placeholder="Es. Ciao, avrei bisogno urgente di questa ora per una verifica scritta. Ti andrebbe di scambiare?")
                    
                    if st.button("Invia Richiesta di Scambio"):
                        st.session_state.scambi.append({
                            "da_prof": utente_attivo,
                            "a_prof": prof_destinatario,
                            "data": data_selezionata,
                            "lab": lab_scambio,
                            "ora": ora_scambio,
                            "messaggio": messaggio_scambio,
                            "stato": "In attesa"
                        })
                        st.success(f"Richiesta inviata correttamente a {prof_destinatario}!")
                        st.info(f"📨 **NOTIFICA EMAIL INVIATA A {prof_destinatario}:** Hai ricevuto una proposta di scambio orario da parte di {utente_attivo}.")
            else:
                st.info("Questo slot è libero, puoi prenotarlo direttamente nella scheda precedente senza fare scambi!")
                
            # Visualizzazione richieste ricevute
            st.markdown("---")
            st.subheader("📥 Richieste di scambio ricevute da te")
            richieste_attive = [s for s in st.session_state.scambi if s["a_prof"] == utente_attivo and s["stato"] == "In attesa"]
            
            if not richieste_attive:
                st.write("Non hai nessuna richiesta di scambio in attesa.")
            else:
                for idx, scambio in enumerate(richieste_attive):
                    st.warning(f"**Da:** {scambio['da_prof']} | **Per il giorno:** {scambio['data']} | **Lab:** {scambio['lab']} | **Ora:** {scambio['ora']}")
                    st.write(f"💬 *Nota del collega:* {scambio['messaggio']}")
                    col_acc, col_rif = st.columns(2)
                    with col_acc:
                        if st.button("Accetta Scambio", key=f"acc_{idx}"):
                            # Logica di scambio effettivo delle prenotazioni
                            chiave_target = (scambio['data'], scambio['lab'], scambio['ora'])
                            # Per semplicità nel prototipo, lo slot passa al richiedente
                            st.session_state.prenotazioni[chiave_target] = {
                                "prof": scambio['da_prof'],
                                "motivo": "Ottenuto da scambio",
                                "stato": "Confermata"
                            }
                            scambio["stato"] = "Accettato"
                            st.success("Scambio accettato! Le prenotazioni sono state aggiornate.")
                            st.info(f"📨 **NOTIFICA EMAIL INVIATA A {scambio['da_prof']}:** Il tuo scambio è stato ACCETTATO.")
                            st.rerun()
                    with col_rif:
                        if st.button("Rifiuta Scambio", key=f"rif_{idx}"):
                            scambio["stato"] = "Rifiutato"
                            st.error("Scambio rifiutato.")
                            st.info(f"📨 **NOTIFICA EMAIL INVIATA A {scambio['da_prof']}:** Il tuo scambio è stato RIFIUTATO.")
                            st.rerun()

        with tab3:
            st.subheader("Riepilogo e Annullamento delle tue prenotazioni")
            mie_prenotazioni = {k: v for k, v in st.session_state.prenotazioni.items() if v["prof"] == utente_attivo}
            
            if not mie_prenotazioni:
                st.write("Non hai prenotazioni registrate a tuo nome.")
            else:
                for chiave, dati in list(mie_prenotazioni.items()):
                    st.write(f"• **Data:** {chiave[0].strftime('%d/%m/%Y')} | **{chiave[1]}** | **{chiave[2]}** -> Attività: {dati['motivo']}")
                    if st.button("Annulla Prenotazione", key=f"del_{chiave}"):
                        del st.session_state.prenotazioni[chiave]
                        st.success("Prenotazione rimossa con successo!")
                        st.info("📨 **NOTIFICA EMAIL INVIATA A TUTTI I PROFESSORI:** Una prenotazione è stata cancellata e lo slot è tornato disponibile.")
                        st.rerun()

    # ==========================================
    # INTERFACCIA 2: STUDENTE
    # ==========================================
    elif ruolo == "Studente":
        st.subheader("🔍 Ricerca rapida per studenti")
        st.info("Visualizzazione in Sola Lettura. Usa i filtri qui sotto per capire dove si trovano le classi o i professori.")
        
        opzione_ricerca = gen_scelta = st.radio("Cosa vuoi cercare?", ["Filtra per Professore", "Filtra per Classe / Materia"])
        
        if opzione_ricerca == "Filtra per Professore":
            prof_cercato = st.selectbox("Seleziona il Professore da cercare:", ["Prof. Rossi", "Prof. Bianchi", "Prof. Verdi"])
            risultati = {k: v for k, v in st.session_state.prenotazioni.items() if v["prof"] == prof_cercato}
            
            if not risultati:
                st.write(f"Nessun laboratorio occupato da **{prof_cercato}** nei dati in memoria.")
            else:
                for k, v in risultati.items():
                    st.write(f"📍 Il giorno **{k[0].strftime('%d/%m/%Y')}** alla **{k[2]}** il professore è nel laboratorio: **{k[1]}** ({v['motivo']})")
                    
        else:
            testo_cercato = st.text_input("Inserisci la tua classe o materia (es. 5A):")
            if testo_cercato:
                risultati = {k: v for k, v in st.session_state.prenotazioni.items() if testo_cercato.lower() in v["motivo"].lower()}
                if not risultati:
                    st.write(f"Nessuna corrispondenza trovata per '{testo_cercato}'.")
                else:
                    for k, v in risultati.items():
                        st.write(f"📖 **{k[0].strftime('%d/%m/%Y')}** alla **{k[2]}** -> **{k[1]}** (Docente: {v['prof']} | Attività: {v['motivo']})")

    # ==========================================
    # INTERFACCIA 3: TECNICO / AMMINISTRATORE
    # ==========================================
    elif ruolo == "Tecnico / Amministratore":
        tab_admin1, tab_admin2 = st.tabs(["🔧 Sospensione & Manutenzioni", "🗄️ Controllo Globale & Storico"])
        
        with tab_admin1:
            st.subheader("Gestione Sospensioni Temporanee (Lavori in corso)")
            st.write("Da qui puoi bloccare un laboratorio per un'ora specifica, impedendo ai professori di prenotarlo.")
            
            lab_manutenzione = st.selectbox("Laboratorio da bloccare:", LABORATORI, key="admin_lab")
            ora_manutenzione = st.selectbox("Ora del blocco:", [slot['ora'] for slot in schema_orario if slot['prenotabile']], key="admin_ora")
            motivo_blocco = st.text_input("Motivo della manutenzione (Obbligatorio):", placeholder="Es. Aggiornamento PC / Riparazione impianto elettrico")
            
            if st.button("Applica Blocco / Sospensione", type="primary"):
                if motivo_blocco.strip() == "":
                    st.error("Devi inserire un motivo valido per la sospensione.")
                else:
                    chiave_m = (data_selezionata, lab_manutenzione, ora_manutenzione)
                    
                    # Se c'era una prenotazione di un prof, la cancelliamo d'ufficio
                    if chiave_m in st.session_state.prenotazioni:
                        prof_compromesso = st.session_state.prenotazioni[chiave_m]['prof']
                        del st.session_state.prenotazioni[chiave_m]
                        st.warning(f"Attenzione: La prenotazione esistente del {prof_compromesso} è stata annullata d'ufficio.")
                        st.info(f"📨 **NOTIFICA EMAIL INVIATA A {prof_compromesso}:** La tua prenotazione è stata ANNULLATA dal tecnico per il seguente motivo: {motivo_blocco}.")
                    
                    # Attiviamo la manutenzione
                    st.session_state.manutenzioni[chiave_m] = motivo_blocco
                    st.success(f"Laboratorio {lab_manutenzione} sospeso alla {ora_manutenzione}.")
                    st.rerun()
                    
            st.markdown("---")
            st.subheader("Blocchi attivi per questo giorno")
            blocchi_giorno = {k: v for k, v in st.session_state.manutenzioni.items() if k[0] == data_selezionata}
            if not blocchi_giorno:
                st.write("Nessuna sospensione programmata per oggi.")
            else:
                for k, v in list(blocchi_giorno.items()):
                    st.write(f"• **{k[1]}** alla **{k[2]}** -> Bloccato per: *{v}*")
                    if st.button("Rimuovi Blocco", key=f"unblock_{k}"):
                        del st.session_state.manutenzioni[k]
                        st.success("Laboratorio riattivato!")
                        st.rerun()

        with tab_admin2:
            st.subheader("Storico e Controllo Globale delle Prenotazioni")
            st.write("In questa sezione puoi visionare tutte le prenotazioni del sistema e cancellarle in caso di emergenza.")
            
            if not st.session_state.prenotazioni:
                st.write("Nessuna prenotazione presente nel sistema in tutta la memoria.")
            else:
                for chiave, dati in list(st.session_state.prenotazioni.items()):
                    col_st1, col_st2 = st.columns([3, 1])
                    with col_st1:
                        st.write(f"📅 **{chiave[0].strftime('%d/%m/%Y')}** | {chiave[1]} | {chiave[2]} -> **Docente:** {dati['prof']} (*{dati['motivo']}*)")
                    with col_st2:
                        if st.button("Cancella d'ufficio", key=f"force_del_{chiave}"):
                            del st.session_state.prenotazioni[chiave]
                            st.success("Annullata!")
                            st.info(f"📨 **NOTIFICA EMAIL INVIATA A {dati['prof']}:** La tua prenotazione è stata revocata dall'Amministratore.")
                            st.rerun()