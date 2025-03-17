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

class ConversationMemory:
    def _init_(self):
        self.messages = []
        
    def save(self, state):
        self.messages = state.get("messages", [])
        
    def load(self):
        return {"messages": self.messages}
    
    def reset_messages(self):
        self.messages = []

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
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()
    if 'cv_data' not in st.session_state:
        st.session_state.cv_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def main():
    initialize_session_state()
    
    st.title("ORIENTA, pronta per assisterti")
    
    # Verifica se i dati della scheda studente sono presenti nella sessione
    if 'form_data' in st.session_state:
        # Assegna cv_data dalla sessione
        cv_data = st.session_state.form_data
        
        # Inizializza o resetta la conversazione
        st.session_state.memory.reset_messages()
        
        # Filtra i dati della scheda studente rimuovendo qualsiasi campo che potrebbe contenere dati binari
        cv_data_filtered = {}
        for key, value in cv_data.items():
            # Salta campi che potrebbero contenere dati binari o immagini
            if key.lower() not in ["immagine", "foto", "avatar", "picture", "image"] and isinstance(value, (str, int, float, bool, list, dict)):
                cv_data_filtered[key] = value

        # Controlla che la dimensione dei dati sia ragionevole
        cv_data_json = json.dumps(cv_data_filtered, indent=2)
        if len(cv_data_json) > 10000:  # Limita la dimensione a 10KB
            # Riduci ulteriormente se necessario
            cv_data_filtered = {k: v for k, v in cv_data_filtered.items() if k in ["nome", "cognome", "titolo_di_studio", "esperienze", "competenze"]}
            cv_data_json = json.dumps(cv_data_filtered, indent=2)

        system_message = {
            "role": "system", 
            "content": f"""
            Sei un simpatico assistente specializzato, ti chiami 'Orienta', sei femmina, nell'orientamento formativo e professionale.
    
            Hai a disposizione queste informazioni sul profilo dell'utente:
    
            {cv_data_json}
            
            Analizza queste informazioni e utilizza la tua conoscenza per:
            1. Dare consigli personalizzati sul percorso formativo più adatto in base ai dati che hai a disposizione, mostrando eventualmente università con i rispettivi siti dei corsi di laurea.
            2. Suggerire opportunità professionali (come: offerte di lavoro su Linkedin o proponi siti e pagine web con cui l'utente possa interfacciarsi)  allineate con il profilo.
            3. Identificare competenze da sviluppare per migliorare l'occupabilità e pianifica le tempistiche per ottenere determinate certificazioni o abilità, mostrando un elenco di enti certificatori e la loro ubicazione.  
            4. Proporre strategie per raggiungere gli obiettivi di carriera.
            
            Rispondi in modo naturale, amichevole, ma professionale, adotta un tono scherzoso e simpatico per aiutare la platea studentesca ad essere a proprio agio nell'interloquire con te. Utilizza la cronologia della conversazione 
            per mantenere il contesto. Se non sei sicuro della richiesta dell'utente, chiedi chiarimenti. Prova ad utilizzare anche battute ironiche per rendere la 
            conversazione più divertente, nel caso utilizza anche emoji e un tono scherzoso. Non generare link che quando cliccati portano a siti web esterni non funzionanti.
            """
        }
        
        # Salva il messaggio nella memoria
        messages = st.session_state.memory.load().get("messages", [])
        messages.append(system_message)
        state = {"messages": messages}
        st.session_state.memory.save(state)
        
        # Visualizza la cronologia della chat
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)
        
        # Input per il messaggio dell'utente
        user_input = st.chat_input("Cosa vorresti sapere sul tuo percorso formativo o lavorativo?")
        
        if user_input:
            # Visualizza il messaggio dell'utente
            st.chat_message("user").write(user_input)
            
            # Aggiorna la cronologia
            st.session_state.chat_history.append(("user", user_input))
            
            # Carica la memoria corrente
            state = st.session_state.memory.load()
            messages = state.get("messages", [])
            
            # Aggiungi il messaggio dell'utente
            messages.append({"role": "user", "content": user_input})

            # Limit the number of messages in the conversation history
            MAX_MESSAGES = 10  # Adjust based on your needs

            # When preparing messages for the model
            if len(messages) > MAX_MESSAGES:
                # Keep system message and the most recent messages
                system_messages = [msg for msg in messages if msg["role"] == "system"]
                recent_messages = messages[-MAX_MESSAGES:]
        
                # Combine system messages with recent messages
                messages = system_messages + [msg for msg in recent_messages if msg["role"] != "system"]

            # Prepara l'input per il modello
            llm = get_llm()
            llm_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    llm_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    llm_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    llm_messages.append(AIMessage(content=msg["content"]))
            
            # Ottieni la risposta dal modello
            with st.chat_message("assistant"):
                with st.spinner("Sto elaborando la risposta..."):
                    response = llm.invoke(llm_messages)
                    ai_response = response.content
                    st.write(ai_response)
            
            # Aggiorna la cronologia
            st.session_state.chat_history.append(("assistant", ai_response))
            
            # Aggiorna la memoria
            messages.append({"role": "assistant", "content": ai_response})
            state["messages"] = messages
            st.session_state.memory.save(state)
    else:
        st.error("Errore: Dati della scheda studente non trovati nella sessione. Assicurati di aver completato il form della scheda studente.")

if __name__ == "__main__":
    main()