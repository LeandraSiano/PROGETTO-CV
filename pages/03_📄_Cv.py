import streamlit as st
import json
import boto3
from langchain_aws import ChatBedrock
from botocore.config import Config
import urllib3
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from streamlit.components.v1 import html
import base64
from PIL import Image
import io

# Carica le variabili d'ambiente
load_dotenv()

# Disabilita avvisi di richieste non sicure
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_llm():
    """Inizializza e restituisce il client Bedrock per Claude."""
    # Verifica che le credenziali siano disponibili e le carica
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_access_key or not aws_secret_key:
        st.error("Credenziali AWS mancanti. Assicurati che il file .env contenga AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY.")
        return None
    
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-west-1',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        verify=False,  # Disabilita la verifica SSL
        config=Config(
            proxies={'https': None}
        )
    )
    
    llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        model_kwargs={
            "temperature": 0.2,  # Bilanciamento tra coerenza e creatività
            "max_tokens": 4000,  # Aumentato per la generazione del CV
        }
    )
    
    return llm

def optimize_image(base64_img, max_size=(150, 150), quality=85):
    """Ottimizza un'immagine in base64 ridimensionandola e comprimendola."""
    try:
        # Decodifica l'immagine base64
        img_data = base64.b64decode(base64_img)
        img = Image.open(io.BytesIO(img_data))
        
        # Ridimensiona l'immagine
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Salva l'immagine con compressione
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        
        # Converti in base64
        new_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return new_base64
    except Exception as e:
        st.warning(f"Errore nell'ottimizzazione dell'immagine: {e}")
        return None

def generate_cv(cv_data, template_style):
    """Genera CV basato sui dati forniti e sullo stile del template."""
    model = get_llm()
    
    # Verifica che il modello sia stato inizializzato correttamente
    if model is None:
        return "<p>Errore: impossibile inizializzare il modello di linguaggio a causa di credenziali mancanti.</p>"
    
    parser = StrOutputParser()
    
    # Crea una copia dei dati del CV per la manipolazione
    cv_data_for_model = cv_data.copy()
    
    has_profile_picture = False
    profile_image_html = ""

    if 'profile_picture' in cv_data_for_model and cv_data_for_model['profile_picture']:
        has_profile_picture = True
    # Ottimizza l'immagine
        optimized_img = optimize_image(cv_data_for_model['profile_picture'])
        if optimized_img:
            profile_image_html = f'<img src="data:image/jpeg;base64,{optimized_img}" alt="Foto Profilo" style="width:150px;height:150px;border-radius:50%;object-fit:cover;">'
        # Rimuovi l'immagine dai dati per il modello
            cv_data_for_model['has_profile_picture'] = True
        else:
            has_profile_picture = False

# Rimuovi l'immagine originale che è troppo grande
    if 'profile_picture' in cv_data_for_model:
        del cv_data_for_model['profile_picture']
    # Riduci la quantità di dati inviati al modello
    reduced_cv_data = {
        "nome": cv_data_for_model.get("nome", ""),
        "cognome": cv_data_for_model.get("cognome", ""),
        "eta": cv_data_for_model.get("eta", ""),
        "email": cv_data_for_model.get("email", ""),
        "numero_telefono": cv_data_for_model.get("numero_telefono", ""),
        "residenza": cv_data_for_model.get("residenza", ""),
        "certificazioni": cv_data_for_model.get("certificazioni", ""),
        "strumenti_software": cv_data_for_model.get("strumenti_software", ""),
        "esperienza_lavorativa": cv_data_for_model.get("esperienza_lavorativa", ""),
        "istruzione": cv_data_for_model.get("istruzione", ""),
        "formazione": cv_data_for_model.get("formazione", ""),
        "tipo_lavoro": cv_data_for_model.get("tipo_lavoro", ""),
        "trasferimento_lavoro": cv_data_for_model.get("trasferimento_lavoro", ""),
        "has_profile_picture": has_profile_picture # Usa il placeholder
    }

    # Definisci prompt per diversi template
    templates = {
    "Modern": """
    You must create a clean, modern CV in HTML format based on the following data:
    json
    {cv_data}
    
     The CV must have:
    - Minimalist and clean design with subtle colour accents
    - Clear and WELL-DEFINED sections
    - Skills displayed as horizontal bar or tag cloud
    - Two-columns layout for efficient use of space
    - Icons for contact information
    - Sections: Profile (personal data), Contacts, Skills, Work experience, Education and training, Interests and preferences
    - Top section with space for profile photo next to 'Profile' section. Include a placeholder {{PROFILE_PICTURE_PLACEHOLDER}} where the photo should go
    - Add an emoji to each section (e.g. 📞 for Contacts, 🎓 for Education)
    - Ignore 'Academic Data'
    - The CV must be written in italian
    -     padding-top: 10px;    /* Padding superiore */
    padding-right: 15px;  /* Padding destro */
    padding-bottom: 20px; /* Padding inferiore */
    padding-left: 25px;   /* Padding sinistro */
    - IMPORTANT: In the Profile section, add this exact HTML code: <div id=\"profile-picture-container\">PROFILE_PICTURE_PLACEHOLDER</div>

    Return ONLY the complete HTML that can be displayed directly, with embedded CSS styling.
    DO NOT include any markdown code blocks, explanations, or introductions.
    DO NOT wrap the HTML in triple backticks.
    DO NOT start with phrases like "Here's the HTML" or "Here's the code".
    Start directly with the HTML tag like <main> or <div> or <html>.
    """,
    
    "Traditional": """
    You must create a traditional, professional CV in HTML format based on the following data:
    json
    {cv_data}
 
    The CV must have:
    - Classic, formal layout (single column)
    - Conservative colour scheme (black, grey, navy blue)
    - Traditional ordering of sections: Profile (personal data), Contacts, Skills, Work experience, Education and training, Interests and preferences
    - Emphasis on work experience history
    - Serif font for a classic appearance
    - Top section with space for profile photo next to 'Profile' section. Include a placeholder {{PROFILE_PICTURE_PLACEHOLDER}} where the photo should go
    - Add an emoji to each section (e.g. 📞 for Contacts, 🎓 for Education)
    - Ignore 'Academic Data'
    - The CV must be written in italian
    -     padding-top: 10px;    /* Padding superiore */
    padding-right: 15px;  /* Padding destro */
    padding-bottom: 20px; /* Padding inferiore */
    padding-left: 25px;   /* Padding sinistro */
    - IMPORTANT: In the Profile section, add this exact HTML code: <div id=\"profile-picture-container\">PROFILE_PICTURE_PLACEHOLDER</div>

    Return ONLY the complete HTML that can be displayed directly, with embedded CSS styling.
    DO NOT include any markdown code blocks, explanations, or introductions.
    DO NOT wrap the HTML in triple backticks.
    DO NOT start with phrases like "Here's the HTML" or "Here's the code".
    Start directly with the HTML tag like <main> or <div> or <html>.
    """,
    
    "Creative": """
    You must create a creative and visually distinctive CV in HTML format based on the following data:
    json
    {cv_data}
    
    The CV must have:
    - Bold use of colours and visual elements
    - Creative layout that highlights achievements
    - Visual representation of skills and experience
    - Customised iconography or visual elements
    - Distinctive typographic choices
    - Sections: Profile (personal details), Contacts, Skills, Work experience, Education and training, Interests and preferences
    - Top section with space for profile photo next to 'Profile' section. Include a placeholder {{PROFILE_PICTURE_PLACEHOLDER}} where the photo should go
    - Add an emoji to each section (e.g. 📞 for Contacts, 🎓 for Education)
    - Ignore 'Academic Data'
    - The CV must be written in italian
    - it must create specific square sections for each category 
    -     padding-top: 10px;    /* Padding superiore */
    padding-right: 15px;  /* Padding destro */
    padding-bottom: 20px; /* Padding inferiore */
    padding-left: 25px;   /* Padding sinistro */
    - IMPORTANT: In the Profile section, add this exact HTML code: <div id=\"profile-picture-container\">PROFILE_PICTURE_PLACEHOLDER</div>

    Return ONLY the complete HTML that can be displayed directly, with embedded CSS styling.
    DO NOT include any markdown code blocks, explanations, or introductions.
    DO NOT wrap the HTML in triple backticks.
    DO NOT start with phrases like "Here's the HTML" or "Here's the code".
    Start directly with the HTML tag like <main> or <div> or <html>.
    """
    }
    
    # Seleziona il template in base allo stile
    prompt_template = templates[template_style]
    
    # Crea il prompt
    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    
    # Crea la catena
    chain = prompt | model | parser
    
    # Genera CV
    try:
        result = chain.invoke({"cv_data": json.dumps(reduced_cv_data)})
        
        # Sostituisci il placeholder con l'HTML dell'immagine
        if has_profile_picture and profile_image_html:
    # Sostituisci il placeholder con l'immagine
            result = result.replace("PROFILE_PICTURE_PLACEHOLDER", profile_image_html)
        else:
    # Se non c'è immagine, rimuovi il placeholder
            result = result.replace("PROFILE_PICTURE_PLACEHOLDER", "")
            result = result.replace('<div id="profile-picture-container"></div>', "")
        
        # Pulizia del risultato
        result = result.strip()
        if not result.startswith("<"):
            # Se non inizia con un tag HTML, cerchiamo di estrarre solo l'HTML
            import re
            html_match = re.search(r'(<[^>]+>[\s\S]*)', result)
            if html_match:
                result = html_match.group(1)
            else:
                st.warning("Il modello ha restituito una risposta che potrebbe non essere HTML puro.")
        
        return result
    except Exception as e:
        return f"<p>Errore durante la generazione del CV: {str(e)}</p>"

# Interfaccia Streamlit
def main():
    st.title("CV Generator")
    st.write("Genera il tuo CV basato sui dati della scheda studente.")
    
    # Verifica se i dati della scheda studente sono presenti nella sessione
    if 'form_data' in st.session_state:
        cv_data = st.session_state.form_data
        
        # Selezione del template
        template_style = st.selectbox(
            "Seleziona uno stile di template CV:",
            ["Modern", "Traditional", "Creative"]
        )
        
        # Pulsante di generazione
        if st.button("Genera CV"):
            with st.spinner("Generazione del tuo CV in corso..."):
                generated_cv = generate_cv(cv_data, template_style)
            
            # Mostra il risultato usando il componente HTML invece di markdown
            st.subheader("CV Generato")
            
            # Salva il CV generato in session_state per eventuali usi futuri
            st.session_state.generated_cv = generated_cv
            
            # Usa st.components.v1.html per renderizzare l'HTML
            html(generated_cv, height=800, scrolling=True)  # Altezza regolabile in base alle necessità
            
            # Pulsante di download
            st.download_button(
                label="Scarica CV come HTML",
                data=generated_cv,
                file_name=f"cv_{template_style.lower()}.html",
                mime="text/html"
            )
    else:
        st.error("Errore: Dati della scheda studente non trovati nella sessione. Assicurati di aver completato il form della scheda studente.")

if __name__ == "__main__":
    main()