import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Chi Siamo - Comune di Napoli",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&display=swap');
    .main-header {
        font-family: 'Oswald', bold;
        font-size: 48px;
        font-weight: bold;
        color: #1E6FBA;
        text-align: center;
        margin-bottom: 30px;
        padding-top: 20px;
    }
    .sub-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 20px;
    }
    .section {
        background-color: #fafafa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .testimonial {
        font-style: bebas neue;
        color: #555;
        margin-bottom: 10px;
        font-size: 18px;
        line-height: 1.5;
    }
    .testimonial-item {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    .testimonial-image {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
    }
    .testimonial-content {
        flex: 1;
    }   
    /* Stile per la sezione Testimonianze */
    .testimonial-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .testimonial-card-image {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 15px;
    }
    .testimonial-card-text {
        font-style: bebas neue;
        color: #444;
        font-size: 16px;
        text-align: center;
        line-height: 1.6;
        padding: 0 10px;
    }
    .testimonial-card-name {
        font-weight: bold;
        margin-top: 10px;
        color: #1E6FBA;
    }
    .contact-info {
        font-size: 18px;
        margin-bottom: 10px;
    }
    /* Complete reset of social icons styling */
    .social-container {
        text-align: center;
    }
    .social-icon {
        display: inline-block;
        margin: 0 10px;
    }
    .social-icon img {
        width: 40px !important;
        height: 40px !important;
        max-width: 40px !important;
        max-height: 40px !important;
        object-fit: contain !important;
    }
    /* Layout orizzontale per le sezioni di testimonianze */
    .horizontal-container {
        display: flex;
        gap: 20px;
    }
    .testimonial-column {
        flex: 1;
    }
    /* Grid per le testimonianze */
    .testimonial-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Titolo principale
st.markdown('<div class="main-header">CHI SIAMO</div>', unsafe_allow_html=True)

# Layout orizzontale per le sezioni di testimonianze
st.markdown('<div class="horizontal-container">', unsafe_allow_html=True)

# Prima colonna: Cosa dicono di Orientiamoci (senza rettangolo)
st.markdown('<div class="testimonial-column">', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Cosa dicono di Orientiamoci</div>', unsafe_allow_html=True)

# Primo testimone - senza rettangolo
st.markdown("""
<div class="testimonial-item">
    <img src="https://th.bing.com/th/id/R.2b0a1d803a5242a71b47d55658285e40?rik=PfJUxHIuhJDfRQ&riu=http%3a%2f%2fwww.culturaeculture.it%2fwp-content%2fuploads%2f2012%2f09%2fT.Tulic-Fotolia-donna.jpg&ehk=v2lRb018lxpFcotQ2mEpFLk7x%2bT4vTR30p2hkKl%2fgq4%3d&risl=1&pid=ImgRaw&r=0" alt="Maria Rossi" class="testimonial-image">
    <div class="testimonial-content">
        <div class="testimonial">"La piattaforma Orientiamoci del Comune di Napoli mi ha aiutato a trovare il percorso formativo più adatto alle mie aspirazioni. I consigli personalizzati hanno fatto davvero la differenza nel mio percorso di studi!" - Maria Rossi </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Secondo testimone - senza rettangolo
st.markdown("""
<div class="testimonial-item">
    <img src="https://thumbs.dreamstime.com/b/ritratto-di-giovane-uomo-bello-sorridente-40530088.jpg" alt="Luca Bianchi" class="testimonial-image">
    <div class="testimonial-content">
        <div class="testimonial">"Grazie a Orientiamoci ho scoperto borse di studio e opportunità formative che non conoscevo. La piattaforma del Comune è stata fondamentale per prendere decisioni informate sul mio futuro accademico." - Luca Bianchi </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Terzo testimone - senza rettangolo
st.markdown("""
<div class="testimonial-item">
    <img src="https://img.freepik.com/premium-photo/smiling-confident-woman-with-arms-crossed-is-standing-gray-background_826801-6430.jpg" alt="Anna Verdi" class="testimonial-image">
    <div class="testimonial-content">
        <div class="testimonial">"Orientiamoci è una risorsa preziosa per tutti gli studenti napoletani. Il supporto ricevuto attraverso la piattaforma mi ha permesso di fare scelte consapevoli sul mio percorso universitario e sulle prime esperienze professionali." - Anna Verdi </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Seconda colonna: Testimonianze (formato verticale)
st.markdown('<div class="testimonial-column">', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Testimonianze</div>', unsafe_allow_html=True)
st.markdown('<div class="testimonial-grid">', unsafe_allow_html=True)

# Primo testimone con testimonianza aggiornata
st.markdown("""
<div class="testimonial-card">
    <img src="https://thumbs.dreamstime.com/b/l%C3%A4chelnder-junger-mann-mit-dem-bart-der-gegen-wei%C3%9Fen-hintergrund-steht-72608454.jpg" alt="Giovanni Esposito" class="testimonial-card-image">
    <div class="testimonial-card-text">
        "Da studente del liceo, ero indeciso su quale università scegliere. La piattaforma Orientiamoci del Comune di Napoli mi ha aiutato a valutare le diverse opzioni in base alle mie attitudini e interessi. Grazie ai suggerimenti ricevuti, ho scelto un percorso di studi che mi appassiona veramente e che offre buone prospettive lavorative nel nostro territorio."
    </div>
    <div class="testimonial-card-name">Giovanni Esposito 🚀</div>
</div>
""", unsafe_allow_html=True)

# Secondo testimone con testimonianza aggiornata
st.markdown("""
<div class="testimonial-card">
    <img src="https://ioadvisory.com/wp-content/uploads/2019/04/Depositphotos_10422883_s-2019.jpg" alt="Francesca Russo" class="testimonial-card-image">
    <div class="testimonial-card-text">
        "Orientiamoci è stata una risorsa fondamentale durante l'ultimo anno di università. Non sapevo come presentarmi nel mondo del lavoro, ma grazie ai consigli sulla stesura del CV e alla panoramica delle opportunità professionali nel territorio napoletano, ho potuto affrontare con maggiore sicurezza i primi colloqui. Oggi lavoro in un'azienda locale e sono grata per il supporto ricevuto dal Comune."
    </div>
    <div class="testimonial-card-name">Francesca Russo 🌟</div>
</div>
""", unsafe_allow_html=True)

# Terzo testimone con testimonianza aggiornata
st.markdown("""
<div class="testimonial-card">
    <img src="https://www.mecagine.com/wp-content/uploads/2019/09/pierre-600.jpg" alt="Marco De Luca" class="testimonial-card-image">
    <div class="testimonial-card-text">
        "Da studente, ho trovato nella piattaforma Orientiamoci uno strumento prezioso per supportarmi nelle scelte formative. I materiali informativi e le guide sui percorsi disponibili nelle scuole e università napoletane mi hanno permesso di avere una visione chiara delle opportunità. Consiglio vivamente a tutti di utilizzare questa risorsa messa a disposizione dal Comune di Napoli."
    </div>
    <div class="testimonial-card-name">Marco De Luca 💼</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chiusura layout orizzontale
st.markdown('</div>', unsafe_allow_html=True)

# Sezione Pagine Social - completely restructured
st.markdown('<div class="sub-header">Seguici sui social</div>', unsafe_allow_html=True)
st.markdown('<div class="social-container">', unsafe_allow_html=True)

# Each social icon is now in its own container with more specific styling
st.markdown("""
<div class="social-icon">
    <a href="https://www.facebook.com/comunedinapoli" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook">
    </a>
</div>
<div class="social-icon">
    <a href="https://www.instagram.com/comunedinapoli" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram">
    </a>
</div>
<div class="social-icon">
    <a href="https://x.com/ComuneNapoli" target="_blank">
        <img src="https://th.bing.com/th/id/OIP.FJka1TP6GsvlkEr4HO_C0wHaGG?rs=1&pid=ImgDetMain">
</div>
<div class="social-icon">
    <a href="https://www.linkedin.com/company/comune-di-napoli/" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn">
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sezione Contatti
st.markdown('<div class="sub-header">Contatti</div>', unsafe_allow_html=True)
st.markdown('<div class="contact-info"><strong>Indirizzo:</strong> Piazza Municipio, 80133 Napoli NA, Italia</div>', unsafe_allow_html=True)
st.markdown('<div class="contact-info"><strong>Telefono:</strong> +39 081 7951111</div>', unsafe_allow_html=True)
st.markdown('<div class="contact-info"><strong>Email:</strong> info@comune.napoli.it</div>', unsafe_allow_html=True)