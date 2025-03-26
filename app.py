import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import base64
import io
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import bcrypt

# Configurazione della pagina
st.set_page_config(
    page_title="App Scheda Studente",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Applicazione di stile personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1E6FBA;
        text-align: center;
        margin-bottom: 30px;
        padding-top: 20px;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 20px;
    }
    .welcome-msg {
        font-size: 20px;
        color: #2E7D32;
        margin-bottom: 20px;
    }
    .section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .btn {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Dati di accesso
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "password123", "studente1": "abc123"}

# Stati dell'applicazione
def initialize_session_state():
    """Inizializza le variabili di stato della sessione se non esistono"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    if 'form_complete' not in st.session_state:
        st.session_state.form_complete = False
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'profile_picture' not in st.session_state:
        st.session_state.profile_picture = None
    if 'page' not in st.session_state:
        st.session_state.page = "landing"

# Funzioni di navigazione
def go_to_login():
    st.session_state.page = "login"

def go_to_register():
    st.session_state.page = "register"

def go_to_landing():
    st.session_state.page = "landing"

def go_to_dashboard():
    st.session_state.page = "dashboard"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.profile_picture = None
    st.session_state.form_complete = False
    st.session_state.file_uploaded = False
    st.session_state.file_data = None
    st.session_state.page = "landing"

import yaml
import bcrypt

def register_user(username, email, first_name, last_name, password):
    # Hash della password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Carica il file YAML esistente o crea uno nuovo se non esiste
    try:
        with open('config.yml', 'r') as file:
            config = yaml.safe_load(file) or {}
    except FileNotFoundError:
        config = {}

    # Aggiungi le informazioni dell'utente
    new_user = {
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': hashed_password
    }
    
    if 'users' not in config:
        config['users'] = []

    # Aggiungi il nuovo utente all'elenco
    config['users'].append(new_user)
    #print( "Config", config)
    # Salva il file YAML con i dati aggiornati
    with open('config.yml', 'w') as file:
        yaml.dump(config, file)

# Esegui la registrazione chiamando la funzione
#register_user('new_user', 'new_user@example.com', 'John', 'Doe', 'securepassword')

def load_credentials():
    try:
        with open('config.yml', 'r') as file:
            config = yaml.safe_load(file) or {}
        return config.get('users', [])
    except FileNotFoundError:
        return []

def authenticate_user(username, password):
    users = load_credentials()
    for user in users:
        if user['username'] == username and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True
    return False

# Funzione per caricare e visualizzare il contenuto del file
def load_file():
    uploaded_file = st.file_uploader("Carica il file 'File pagella e feedback'", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                file_data = pd.read_excel(uploaded_file)
            else:
                 try:
                    file_data = pd.read_csv(uploaded_file, encoding='utf-8', delimiter=';')
                 except UnicodeDecodeError:
                    file_data = pd.read_csv(uploaded_file, encoding='latin-1')
            
            # Converti i nomi delle colonne in stringhe
            file_data.columns = [str(col) for col in file_data.columns]
            
            # Verifica se il file contiene colonne
            if file_data.empty or file_data.shape[1] == 0:
                st.error("Errore durante il caricamento del file: il file non contiene colonne valide.")
                return None
                
            
            st.success("File caricato con successo!")
            st.session_state.file_uploaded = True
            st.session_state.file_data = file_data
            print(file_data)
            return file_data
        except Exception as e:
            st.error(f"Errore durante il caricamento del file: {e}")
            return None
    else:
        return None

# Funzione per creare una scheda dello studente
def create_student_profile(file_data, form_data, profile_picture=None):
    file_data_str_keys = {str(key): value for key, value in file_data.items()}
    
    scheda = {
        "Dati Personali": {
            "Nome": form_data["nome"],
            "Cognome": form_data["cognome"],
            "Età": form_data["eta"],
            
        },
        
        "Contatti": {
            "Email": form_data["email"],
            "Numero di telefono": form_data["numero_telefono"],
            "Residenza": form_data["residenza"]

        },
        "Competenze": {
            "Certificazioni": form_data["certificazioni"],
            "Strumenti Software": form_data["strumenti_software"],
            "Certificazioni Lingue": form_data["certificazioni_lingue"],
            "Soft Skills": form_data["soft_skills"]
        },
        "Esperienze Lavorative":{
            "Esperienza Lavorativa": form_data["esperienza_lavorativa"]
        },
        "Istruzione e Formazione":{
            "Istruzione": form_data["istruzione"],
            "Formazione": form_data["formazione"]
        },
        "Interessi e Preferenze": {
            "Materia Preferita": form_data["materia_preferita"],
            "Materia Meno Preferita": form_data["materia_meno_preferita"],
            "Passioni": form_data["passioni"],
            "Musica": form_data["musica"]
        },
        "Lingue e Informatica": {
            "Interesse Lingue Straniere": form_data["lingue_straniere"],
            "Lingue da Approfondire": form_data["lingue_approfondire"],
            "Interesse Informatica": form_data["informatica"]
        },
        "Obiettivi Professionali": {
            "Settore Lavorativo": form_data["settore_lavoro"],
            "Obiettivi a Breve Termine": form_data["obiettivi_breve"],
            "Obiettivi a Lungo Termine": form_data["obiettivi_lungo"],
            "Tipo di Lavoro": form_data["tipo_lavoro"],
            "Disponibilità al Trasferimento": form_data["trasferimento_lavoro"]
        },
        "Formazione Continua": {
            "Corsi Online": form_data["corsi_online"],
            "Programmi di Stage": form_data["programma_stage"]
        },
        "Dati Accademici": file_data_str_keys
    }
    
    if profile_picture:
        # Convertire l'immagine in base64 per il salvataggio
        buffered = io.BytesIO()
        profile_picture.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        scheda["Immagine Profilo"] = img_str
    
    return scheda

def save_form_data(username, form_data, profile_picture=None):
    try:
        with open('user_data.yml', 'r') as file:
            user_data = yaml.safe_load(file) or {}
    except FileNotFoundError:
        user_data = {}

    user_data[username] = form_data
   
    if profile_picture:
        buffered = io.BytesIO()
        profile_picture.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        user_data[username]['profile_picture'] = img_str

    with open('user_data.yml', 'w') as file:
        yaml.dump(user_data, file)

def load_form_data(username):
    try:
        with open('user_data.yml', 'r') as file:
            user_data = yaml.safe_load(file) or {}
        return user_data.get(username, {})
    except FileNotFoundError:
        return {}

# Interfaccia principale
def main():
    initialize_session_state()
    # Sidebar per la navigazione (visibile solo se loggati)
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown('<div class="sub-header">Menu di Navigazione</div>', unsafe_allow_html=True)
            
            # Visualizza l'immagine del profilo se presente
            if st.session_state.profile_picture is not None:
                st.image(st.session_state.profile_picture, width=150)
            
            st.markdown(f'<div class="welcome-msg">Benvenuto, {st.session_state.username}!</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.button("Il mio profilo", on_click=go_to_dashboard)
            
            progress_col1, progress_col2 = st.columns(2)
            with progress_col1:
                st.markdown("Form completato:")
            with progress_col2:
                if st.session_state.form_complete:
                    st.markdown("✅")
                else:
                    st.markdown("❌")
                    
            progress_col1, progress_col2 = st.columns(2)
            with progress_col1:
                st.markdown("File caricato:")
            with progress_col2:
                if st.session_state.file_uploaded:
                    st.markdown("✅")
                else:
                    st.markdown("❌")
            
            st.markdown("---")
            #st.button("Genera CV", on_click=lambda: st.session_state.page = "cv")
            #st.button("Contatti", on_click=lambda: st.session_state.page = "contatti")
            st.button("Logout", on_click=logout)
    
    # Pagina di destinazione
    if st.session_state.page == "landing":
        st.markdown('<div class="main-header">📚 ORIENTIAMOCI 📚 </div>', unsafe_allow_html=True)

        # Contenitore principale con immagine e bottoni
        main_col1, main_col2 = st.columns([2, 1])
        
        with main_col1:
            st.markdown("""
            <div class="section">
                <h2>Benvenuto in ORIENTIAMOCI</h2>
                <p>Questa applicazione ti consente di:</p>
                <ul>
                    <li>Creare un profilo personale</li>
                    <li>Chiedere suggerimenti ad una Chat</li>
                    <li>Generare un CV</li>
                </ul>
                <p>Per iniziare, accedi o registrati utilizzando i pulsanti sulla destra.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with main_col2:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.button("ACCEDI", on_click=go_to_login, key="btn_login", use_container_width=True)
            st.button("REGISTRATI", on_click=go_to_register, key="btn_register", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Pagina di login
    elif st.session_state.page == "login":
        st.markdown('<div class="main-header">Accesso al Sistema</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            username = st.text_input("Nome utente")
            password = st.text_input("Password", type="password")
            
            login_col1, login_col2 = st.columns([1, 1])
            
            with login_col1:
                if st.button("ACCEDI", key="submit_login"):
                    if authenticate_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.form_data = load_form_data(username)
                        go_to_dashboard()
                        st.rerun()
                    else:
                        st.error("Nome utente o password errati")
            with login_col2:
                if st.button("Torna indietro", key="back_to_landing"):
                    go_to_landing()
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Pagina di registrazione
    elif st.session_state.page == "register":
        st.markdown('<div class="main-header">Registrazione Nuovo Utente</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            new_username = st.text_input("Nuovo nome utente")
            new_password = st.text_input("Nuova password", type="password")
            confirm_password = st.text_input("Conferma password", type="password")
            
            reg_col1, reg_col2 = st.columns([1, 1])
            
            with reg_col1:
                if st.button("REGISTRATI", key="submit_register"):
                    if not new_username or not new_password:
                        st.error("Compila tutti i campi!")
                    elif new_password != confirm_password:
                        st.error("Le password non coincidono!")
                    elif new_username in st.session_state.users:
                        st.error("Nome utente già esistente!")
                    else:
                        register_user(new_username, "", "", "", new_password)
                        st.success("Registrazione completata! Ora puoi accedere")
                        st.session_state.username = new_username
                        st.session_state.logged_in = True
                        go_to_dashboard()
                        st.rerun()
            with reg_col2:
                if st.button("Torna indietro", key="back_to_landing_reg"):
                    go_to_landing()
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Dashboard utente
    elif st.session_state.page == "dashboard" and st.session_state.logged_in:
        st.markdown('<div class="main-header">Profilo Studente</div>', unsafe_allow_html=True)
        
        # Tabs per organizzare le diverse sezioni
        tab1, tab2, tab3 = st.tabs(["Dati Personali", "Carica File", "Scheda Completa"])
        
        # Tab 1: Dati Personali
        with tab1:
            st.markdown('<div class="sub-header">Informazioni Personali e Accademiche</div>', unsafe_allow_html=True)
            
            # Caricamento immagine profilo
            profile_col1, profile_col2 = st.columns([1, 2])
            
            with profile_col1:
                #st.markdown('<div class="section">', unsafe_allow_html=True)
                st.subheader("Immagine Profilo")
                uploaded_image = st.file_uploader("Carica la tua immagine profilo", type=["jpg", "jpeg", "png"])
                
                if uploaded_image is not None:
                    image = Image.open(uploaded_image)
                    st.image(image, width=200)
                    st.session_state.profile_picture = image
                elif 'profile_picture' in st.session_state.form_data:
                    img_str = st.session_state.form_data['profile_picture']
                    image = Image.open(io.BytesIO(base64.b64decode(img_str)))
                    st.image(image, width=200)
                    st.session_state.profile_picture = image
                st.markdown('</div>', unsafe_allow_html=True)
            
            with profile_col2:
                #st.markdown('<div class="section">', unsafe_allow_html=True)
                # Form per i dati personali
                with st.form(key='form_studente'):
                    # Campi obbligatori del profilo
                    st.subheader("Informazioni di Base")
                    form_data = st.session_state.form_data if 'form_data' in st.session_state else {}

                    nome = st.text_input('Nome', value=form_data.get('nome', ''))
                    cognome = st.text_input('Cognome', value=form_data.get('cognome', ''))
                    eta = st.number_input('Età', min_value=0, max_value=120, step=1, value=form_data.get('eta', 0))
                    email = st.text_input('Email', value=form_data.get('email', ''))
                    numero_telefono = st.text_input('Numero di Telefono', value=form_data.get('numero_telefono', ''))
                    residenza = st.text_input('Residenza', value=form_data.get('residenza', ''))
                    certificazioni = st.text_area("Certificazioni Ottenute", value=form_data.get('certificazioni', ''))
                    strumenti_software = st.text_area('Quali strumenti software o tecnologie conosci meglio?', value=form_data.get('strumenti_software', ''))
                    certificazioni_lingue = st.text_input("Certificazioni Lingue Ottenute", value=form_data.get('certificazioni_lingue', ''))
                    soft_skills = st.text_input("Soft Skills", value=form_data.get('soft_skills', ''))
                    esperienza_lavorativa = st.text_area('Quali esperienze lavorative hai?', value=form_data.get('esperienza_lavorativa', ''))
                    formazione = st.text_area('Hai partecipato a Corsi Online o Academy? Se si, quali?', value=form_data.get('formazione', ''))
                    istruzione = st.text_area('Che livello di istruzione hai?', value=form_data.get('istruzione', ''))
                    materia_preferita = st.text_input('Qual è la tua materia preferita?', value=form_data.get('materia_preferita', ''))
                    materia_meno_preferita = st.text_input('Qual è la materia che ti piace di meno?', value=form_data.get('materia_meno_preferita', ''))
                    passioni = st.text_area('Quali passioni hai?', value=form_data.get('passioni', ''))
                    lingue_straniere = st.selectbox('Ti piacciono le lingue straniere?', ['Sì', 'No'], index=0 if form_data.get('lingue_straniere', 'Sì') == 'Sì' else 1)
                    lingue_approfondire = st.multiselect('Quale lingua ti piacerebbe approfondire?', ['Inglese', 'Francese', 'Spagnolo', 'Tedesco', 'Cinese'], default=form_data.get('lingue_approfondire', []))
                    informatica = st.selectbox('Sei appassionato all\'informatica?', ['Sì', 'No'], index=0 if form_data.get('informatica', 'Sì') == 'Sì' else 1)
                    musica = st.text_area('Che musica ti piace?', value=form_data.get('musica', ''))
                    corsi_online = st.text_input('Hai completato corsi online o certificazioni aggiuntive? Se si quali?', value=form_data.get('corsi_online', ''))
                    programma_stage = st.selectbox('Hai completato o stai completando un programma di scambio o stage?', ['Sì', 'No'], index=0 if form_data.get('programma_stage', 'No') == 'Sì' else 1)
                    settore_lavoro = st.text_input('In che settore vorresti lavorare dopo la laurea?', value=form_data.get('settore_lavoro', ''))
                    obiettivi_breve = st.text_area('Quali sono i tuoi obiettivi professionali a breve termine (1-2 anni)?', value=form_data.get('obiettivi_breve', ''))
                    obiettivi_lungo = st.text_area('Quali sono i tuoi obiettivi professionali a lungo termine (5-10 anni)?', value=form_data.get('obiettivi_lungo', ''))
                    tipo_lavoro = st.text_input('Qual è il tipo di lavoro che ti interessa di più? (es. tempo pieno, part-time, remoto, freelance)', value=form_data.get('tipo_lavoro', ''))
                    trasferimento_lavoro = st.selectbox('Sei disposto a trasferirti per lavoro?', ['Sì', 'No', 'Indeciso'], index=0 if form_data.get('trasferimento_lavoro', 'Indeciso') == 'Sì' else (1 if form_data.get('trasferimento_lavoro', 'Indeciso') == 'No' else 2))
                    submit_button = st.form_submit_button(label='SALVA DATI')
                
                if submit_button:
                    # Verifica che tutti i campi obbligatori siano compilati
                    if not nome or not cognome or not email or not formazione:
                        st.error("Per favore, compila tutti i campi obbligatori!")
                    else:
                        # Crea un dizionario con i dati del modulo
                        form_data = {
                            "nome": nome,
                            "cognome": cognome,
                            "eta": eta,
                            "numero_telefono": numero_telefono,
                            "email": email,
                            "residenza": residenza,
                            "certificazioni": certificazioni,
                            "strumenti_software": strumenti_software,
                            "certificazioni_lingue": certificazioni_lingue,
                            "soft_skills": soft_skills,
                            "esperienza_lavorativa": esperienza_lavorativa,
                            "formazione": formazione,
                            "istruzione": istruzione,
                            "materia_preferita": materia_preferita,
                            "materia_meno_preferita": materia_meno_preferita,
                            "passioni": passioni,
                            "lingue_straniere": lingue_straniere,
                            "lingue_approfondire": lingue_approfondire,
                            "informatica": informatica,
                            "musica": musica,
                            "corsi_online": corsi_online,
                            "programma_stage": programma_stage,
                            "settore_lavoro": settore_lavoro,
                            "obiettivi_breve": obiettivi_breve,
                            "obiettivi_lungo": obiettivi_lungo,
                            "tipo_lavoro": tipo_lavoro,
                            "trasferimento_lavoro": trasferimento_lavoro
                        }
                        
                        # Salva i dati nella sessione
                        st.session_state.form_data = form_data
                        st.session_state.form_complete = True
                        # salva i dati dell'utente
                        save_form_data(st.session_state.username, form_data, st.session_state.profile_picture)
                        st.success("Dati salvati con successo!")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 2: Carica File
        with tab2:
            st.markdown('<div class="sub-header">Carica Documenti Accademici</div>', unsafe_allow_html=True)
            st.markdown('<div class="section">', unsafe_allow_html=True)
            
            file_data = load_file()
            
            #if file_data is not None:
             #   st.markdown("### Anteprima del file caricato")
              #  st.dataframe(file_data, use_container_width=True)
            
            #st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 3: Scheda Completa
        with tab3:
            st.markdown('<div class="sub-header">Genera Scheda Studente</div>', unsafe_allow_html=True)
            st.markdown('<div class="section">', unsafe_allow_html=True)
            
            if not st.session_state.form_complete:
                st.warning("Devi prima completare il modulo con i tuoi dati personali nella scheda 'Dati Personali'.")
            elif not st.session_state.file_uploaded:
                st.warning("Devi caricare il file accademico nella scheda 'Carica File'.")
            else:
                if st.button("GENERA SCHEDA STUDENTE"):
                    scheda_studente = create_student_profile(
                        st.session_state.file_data.to_dict(), 
                        st.session_state.form_data,
                        st.session_state.profile_picture
                    )
                    
                    # Mostra un'anteprima della scheda
                    st.markdown("### Scheda Studente")
                    
                    # Visualizza le principali sezioni della scheda
                    st.markdown("#### 📋 Dati Personali")
                    st.write(f"Nome: {scheda_studente['Dati Personali']['Nome']} {scheda_studente['Dati Personali']['Cognome']}")
                    st.write(f"Età: {scheda_studente['Dati Personali']['Età']}")

                    if "Immagine Profilo" in scheda_studente:
                        img_str = scheda_studente["Immagine Profilo"]
                        image = Image.open(io.BytesIO(base64.b64decode(img_str)))
                        st.image(image, width=200)

                    st.markdown("#### 📱 Contatti")
                    st.write(f"Email: {scheda_studente['Contatti']['Email']}")
                    st.write(f"Telefono: {scheda_studente['Contatti']['Numero di telefono']}")
                    st.write(f"Residenza: {scheda_studente['Contatti']['Residenza']}")
                    
                    st.markdown("#### 🗣️ Competenze")
                    st.write(f"Certificazioni: {scheda_studente['Competenze']['Certificazioni']}")
                    st.write(f"Strumenti Software: {scheda_studente['Competenze']['Strumenti Software']}")
                    st.write(f"Certificazioni Lingue: {scheda_studente['Competenze']['Certificazioni Lingue']}")
                    st.write(f"Soft Skills: {scheda_studente['Competenze']['Soft Skills']}")

                    st.markdown("#### 💼 Esperienze Lavorative")
                    st.write(f"Esperienza Lavorativa: {scheda_studente['Esperienze Lavorative']['Esperienza Lavorativa']}")

                    st.markdown("#### 🎓 Istruzione e Formazione")
                    st.write(f"Istruzione: {scheda_studente['Istruzione e Formazione']['Istruzione']}")
                    st.write(f"Formazione: {scheda_studente['Istruzione e Formazione']['Formazione']}")

                    st.markdown("#### 🎯 Obiettivi Professionali")
                    st.write(f"Settore Lavorativo: {scheda_studente['Obiettivi Professionali']['Settore Lavorativo']}")
                    st.write(f"Obiettivi a Breve Termine: {scheda_studente['Obiettivi Professionali']['Obiettivi a Breve Termine']}")
                    
                    # Salva la scheda dello studente in un file JSON
                    if not os.path.exists('schede_studenti'):
                        os.makedirs('schede_studenti')
                    
                    filename = f"schede_studenti/scheda_{scheda_studente['Dati Personali']['Nome']}_{scheda_studente['Dati Personali']['Cognome']}.json"
                    
                    with open(filename, 'w') as f:
                        json.dump(scheda_studente, f, indent=4)
                    
                    st.success(f"Scheda salvata con successo nel file: {filename}")
                    
                    # Offri la possibilità di scaricare il file
                    with open(filename, "r") as file:
                        st.download_button(
                            label="Scarica Scheda Studente (JSON)",
                            data=file,
                            file_name=f"scheda_{scheda_studente['Dati Personali']['Nome']}_{scheda_studente['Dati Personali']['Cognome']}.json",
                            mime="application/json"
                        )
            
            st.markdown('</div>', unsafe_allow_html=True)

# Esecuzione dell'applicazione
if __name__ == "__main__":
    main()