import os
import streamlit as st
import boto3
from botocore.config import Config
import urllib3
from datetime import datetime
import uuid
import json
import pandas as pd
from io import StringIO

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Assistente Carriera",
    page_icon="📝",
    layout="wide"
)

def get_llm():
    # Disabilita avvisi SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Inizializza client AWS Bedrock
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-west-1',
        aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
        verify=False,  # Disabilita verifica SSL
        config=Config(
            proxies={'https': None}
        )
    )

    # Definisci modello LLM
    model = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    )

    return model

def initialize_session_state():
    """Inizializza le variabili di stato della sessione se non esistono"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'form_data' not in st.session_state:
        st.session_state.form_data = None
    if 'last_user_input' not in st.session_state:
        st.session_state.last_user_input = None

def extract_all_student_data(cv_data):
    """Estrai tutti i dati importanti dalla scheda studente"""
    if not cv_data:
        return {}
    
    # Converto materie preferite/meno preferite in arrays
    if "materia_preferita" in cv_data and "materie_preferite" not in cv_data:
        cv_data["materie_preferite"] = [cv_data["materia_preferita"]]
    
    if "materia_meno_preferita" in cv_data and "materie_meno_preferite" not in cv_data:
        cv_data["materie_meno_preferite"] = [cv_data["materia_meno_preferita"]]
    
    # Mappatura dei campi dalla scheda studente
    student_data = {
        "nome": cv_data.get("nome", "Studente"),
        "cognome": cv_data.get("cognome", ""),
        "eta": cv_data.get("eta", 20),
        "email": cv_data.get("email", ""),
        "numero_telefono": cv_data.get("numero_telefono", ""),
        "residenza": cv_data.get("residenza", ""),
        "background": cv_data.get("istruzione", "Non specificato"),
        "certificazioni": cv_data.get("certificazioni", ""),
        "strumenti_software": cv_data.get("strumenti_software", ""),
        "certificazioni_lingue": cv_data.get("certificazioni_lingue", ""),
        "soft_skills": cv_data.get("soft_skills", ""),
        "competenze": cv_data.get("strumenti_software", "").split(", ") if cv_data.get("strumenti_software") else [],
        "esperienza_lavorativa": cv_data.get("esperienza_lavorativa", "Nessuna esperienza specificata"),
        "istruzione": cv_data.get("istruzione", "Non specificata"),
        "formazione": cv_data.get("formazione", "Non specificata"),
        "interessi": cv_data.get("passioni", "Non specificati"),
        "materie_preferite": cv_data.get("materie_preferite", [cv_data.get("materia_preferita", "Non specificata")]),
        "materie_meno_preferite": cv_data.get("materie_meno_preferite", [cv_data.get("materia_meno_preferita", "Non specificata")]),
        "passioni": cv_data.get("passioni", "Non specificate"),
        "tipo_lavoro": cv_data.get("tipo_lavoro", "Non specificato"),
        "trasferimento_lavoro": cv_data.get("trasferimento_lavoro", "Non specificato"),
        "lingue_straniere": cv_data.get("lingue_straniere", ""),
        "lingue_approfondire": cv_data.get("lingue_approfondire", []),
        "informatica": cv_data.get("informatica", ""),
        "settore_lavoro": cv_data.get("settore_lavoro", ""),
        "obiettivi_breve": cv_data.get("obiettivi_breve", ""),
        "obiettivi_lungo": cv_data.get("obiettivi_lungo", "")
    }
    
    return student_data

def create_system_prompt(student_data):
    """Crea il prompt di sistema in base ai dati dello studente"""
    return f"""Sei Orienta, un'assistente specializzata in orientamento educativo e professionale. Ecco il profilo dello studente:

Nome: {student_data.get('nome', 'Non specificato')}
Cognome: {student_data.get('cognome', 'Non specificato')}
Età: {student_data.get('eta', 'Non specificata')}
Email: {student_data.get('email', 'Non specificata')}
Numero telefono: {student_data.get('numero_telefono', 'Non specificato')}
Residenza: {student_data.get('residenza', 'Non specificata')}
Background: {student_data.get('background', 'Non specificato')}
Istruzione: {student_data.get('istruzione', 'Non specificata')}
Formazione: {student_data.get('formazione', 'Non specificata')}
Competenze: {', '.join(student_data.get('competenze', ['Non specificate']))}
Certificazioni: {student_data.get('certificazioni', 'Non specificate')}
Certificazioni lingue: {student_data.get('certificazioni_lingue', 'Non specificate')}
Soft skills: {student_data.get('soft_skills', 'Non specificate')}
Esperienza lavorativa: {student_data.get('esperienza_lavorativa', 'Non specificata')}
Interessi: {student_data.get('interessi', 'Non specificati')}
Materie preferite: {', '.join(student_data.get('materie_preferite', ['Non specificate']))}
Materie meno preferite: {', '.join(student_data.get('materie_meno_preferite', ['Non specificate']))}
Passioni: {student_data.get('passioni', 'Non specificate')}
Tipo di lavoro desiderato: {student_data.get('tipo_lavoro', 'Non specificato')}
Disponibilità a trasferirsi: {student_data.get('trasferimento_lavoro', 'Non specificata')}
Ti piacciono le lingue straniere: {student_data.get('lingue_straniere', 'Non specificato')}
Lingue da approfondire: {', '.join(student_data.get('lingue_approfondire', ['Non specificate']))}
Appassionato di informatica: {student_data.get('informatica', 'Non specificato')}
Settore lavorativo: {student_data.get('settore_lavoro', 'Non specificato')}
Obiettivi a breve termine: {student_data.get('obiettivi_breve', 'Non specificati')}
Obiettivi a lungo termine: {student_data.get('obiettivi_lungo', 'Non specificati')}

Quando rispondi a domande sul background, competenze, interessi o materie preferite/meno preferite dello studente, usa SEMPRE queste informazioni.
Dai consigli personalizzati su percorsi educativi e opportunità professionali. Identifica competenze da sviluppare.
Usa un tono amichevole e professionale, con emoji e umorismo appropriato.
NON DIMENTICARE le materie preferite dello studente quando ti vengono chieste!
"""

def main():
    initialize_session_state()
    
    st.title("ORIENTA, pronta per assisterti")
    
    # Verifica se i dati della scheda studente sono presenti nella sessione
    if 'form_data' in st.session_state and st.session_state.form_data:
        # Assegna cv_data dalla sessione
        cv_data = st.session_state.form_data
        
        # Debug - visualizza i dati disponibili (nascosto dall'interfaccia)
        #with st.expander("Debug", expanded=False):
            #st.checkbox("Mostra dati della scheda studente", key="debug_checkbox", value=False)
            #if st.session_state.debug_checkbox:
             #   st.json(cv_data)
        
        # Estrai tutti i dati dello studente con valori predefiniti per i campi mancanti
        student_data = extract_all_student_data(cv_data)
        
        # Crea il prompt di sistema
        system_prompt = create_system_prompt(student_data)
        
        # Inizializza la chat se è vuota
        if not st.session_state.chat_history:
            welcome_message = f"Ciao {student_data.get('nome', '')}! Sono Orienta, la tua assistente per l'orientamento educativo e professionale. Come posso aiutarti oggi? 😊"
            st.session_state.chat_history.append(("assistant", welcome_message))
        
        # Visualizza la cronologia della chat
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)
        
        # Input per il messaggio dell'utente
        user_input = st.chat_input("Cosa vorresti sapere sul tuo percorso formativo o lavorativo?")
        
        if user_input:
            # Salviamo l'input dell'utente per riutilizzarlo in caso di errore
            st.session_state.last_user_input = user_input
            
            # Visualizza il messaggio dell'utente
            st.chat_message("user").write(user_input)
            
            # Aggiorna la cronologia
            st.session_state.chat_history.append(("user", user_input))
            
            # Ottieni la cronologia della chat per il contesto
            chat_context = ""
            for role, message in st.session_state.chat_history[-6:]:  # Ultimi 6 messaggi
                prefix = "Utente: " if role == "user" else "Orienta: "
                chat_context += f"{prefix}{message}\n\n"
            
            # Ottieni la risposta dal modello - approccio semplificato con un unico messaggio
            with st.chat_message("assistant"):
                with st.spinner("Sto elaborando la risposta..."):
                    try:
                        # Ottieni il modello
                        llm = get_llm()
                        
                        # Crea un singolo messaggio di sistema che include il contesto della chat
                        combined_prompt = f"""
{system_prompt}

CONTESTO DELLA CONVERSAZIONE RECENTE:
{chat_context}

Ora rispondi all'ultimo messaggio dell'utente in modo naturale e informativo, come se stessi continuando la conversazione.
"""
                        # Invia un unico messaggio di sistema seguito da un messaggio utente
                        messages = [
                            SystemMessage(content=combined_prompt),
                            HumanMessage(content=user_input)
                        ]
                        
                        # Chiamata al modello
                        response = llm.invoke(messages)
                        ai_response = response.content
                        
                        # Mostra la risposta
                        st.write(ai_response)
                        
                        # Aggiorna la cronologia
                        st.session_state.chat_history.append(("assistant", ai_response))
                        
                    except Exception as e:
                        st.error(f"Si è verificato un errore: {str(e)}")
                        with st.expander("Dettagli errore", expanded=True):
                            st.write(str(e))
                            
                        # Retry con un approccio ancora più semplice in caso di errore
                        try:
                            # Ottieni il modello
                            llm = get_llm()
                            
                            # Crea un nuovo messaggio con solo il prompt essenziale
                            minimal_prompt = f"""
Sei Orienta, un'assistente per l'orientamento educativo. Lo studente si chiama {student_data.get('nome')} {student_data.get('cognome')}.
Le materie preferite dello studente sono: {', '.join(student_data.get('materie_preferite', ['Non specificate']))}.
Le materie meno preferite sono: {', '.join(student_data.get('materie_meno_preferite', ['Non specificate']))}.
"""
                            # Invia un unico messaggio di sistema seguito da un messaggio utente
                            messages = [
                                SystemMessage(content=minimal_prompt),
                                HumanMessage(content=user_input)
                            ]
                            
                            # Chiamata al modello
                            response = llm.invoke(messages)
                            ai_response = response.content
                            
                            # Mostra la risposta
                            st.write(ai_response)
                            
                            # Aggiorna la cronologia
                            st.session_state.chat_history.append(("assistant", ai_response))
                            
                        except Exception as e2:
                            st.error(f"Secondo errore: {str(e2)}")
                            st.write("Mi dispiace, non sono riuscita a generare una risposta. Prova con una domanda diversa.")
                            
                            # Non aggiungiamo nulla alla cronologia in caso di doppio errore
                            # E rimuoviamo l'ultima domanda dell'utente per non creare inconsistenze
                            if st.session_state.chat_history[-1][0] == "user":
                                st.session_state.chat_history.pop()
    else:
        st.error("Errore: Dati della scheda studente non trovati nella sessione. Assicurati di aver completato il form della scheda studente.")
        
        # Opzione di debug per caricare dati di test (nascosta)
        #with st.expander("Debug Options", expanded=False):
            #if st.button("Carica dati di test"):
                #st.session_state.form_data = {
               # }
                #st.success("Dati di test caricati! Ricarica la pagina.")

if __name__ == "__main__":
    main()