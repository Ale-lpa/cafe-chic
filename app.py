import streamlit as st
import openai

# --- 1. CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_RESTAURANTE = "Nombre de<br>Tu Local" 
ESLOGAN = "EXPERIENCIA GASTRONÓMICA"
# Imagen de fondo elegante (Terraza Mediterránea)
FONDO_URL = "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?q=80&w=2070&auto=format&fit=crop"
# Logo transparente por defecto para evitar errores visuales
LOGO_URL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" 

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LocalMind AI", layout="wide")

# --- 3. ESTÉTICA DE ALTA GAMA ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    
    .stApp {{
        background-image: url("{FONDO_URL}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center center;
    }}
    
    /* Overlay oscuro para mejorar legibilidad del texto */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.2);
        z-index: -1;
    }}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 230px !important;
        max-width: 100% !important;
    }}

    /* Limpieza total de recuadros de error */
    [data-testid="stImage"] {{ background: transparent !important; }}
    [data-testid="stImage"] div {{ display: none !important; }}

    /* Chat: Texto blanco con sombra intensa */
    .stChatMessage [data-testid="stMarkdownContainer"] p {{
        font-weight: 800 !important;
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9); 
    }}

    .logo-container {{ position: absolute; left: 15px; top: 35px; z-index: 100; }}

    /* Cabecera en la barandilla */
    .header-right-box {{
        text-align: right; width: 100%;
        margin-top: -125px; padding-right: 20px;
    }}

    .restaurant-title {{
        font-family: 'Playfair Display', serif;
        color: #002147; /* Azul Marino LocalMind */
        font-size: 60px; font-weight: 700;
        line-height: 0.85; margin: 0;
    }}
    
    .restaurant-subtitle {{
        color: #C5A059; /* Dorado */
        letter-spacing: 5px; font-size: 15px;
        font-weight: 900 !important;
        border-top: 2px solid #002147;
        display: inline-block;
        margin-top: 8px; padding-top: 5px;
        text-transform: uppercase;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}

    .stChatInputContainer {{ background-color: transparent !important; padding-bottom: 25px !important; }}

    /* Footer LocalMind */
    .sticky-footer-container {{
        position: fixed; left: 0; bottom: 110px; width: 100%; text-align: center; z-index: 100;
        background: linear-gradient(to top, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 100%);
        padding-bottom: 15px;
    }}

    .brand-line {{ color: #FFFFFF !important; font-weight: 900; font-size: 16px; text-shadow: 2px 2px 4px #000; }}
    .footer-link {{ color: #C5A059 !important; text-decoration: none; font-weight: 900; font-size: 15px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CABECERA ---
col_logo, col_text = st.columns([1, 3])
with col_logo:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(LOGO_URL, width=110)
    st.markdown('</div>', unsafe_allow_html=True)

with col_text:
    st.markdown(f'<div class="header-right-box"><p class="restaurant-title">{NOMBRE_RESTAURANTE}</p><p class="restaurant-subtitle">{ESLOGAN}</p></div>', unsafe_allow_html=True)

# --- 5. ASISTENTE CON ESCRITURA EN TIEMPO REAL ---
SYSTEM_PROMPT = f"Eres el sumiller de {NOMBRE_RESTAURANTE}. Ofrece precios, vinos y maridajes en el idioma del cliente. Powered by LocalMind."

if "messages" not in st.session_state: st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🐟" if message["role"] == "user" else "⚓"):
        st.markdown(message["content"])

if prompt := st.chat_input("Hable con el asistente..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🐟"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚓"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # STREAMING activado para el efecto de escritura
        stream = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages, 
            stream=True
        )
        full_response = st.write_stream(stream) # Esto genera la animación
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- 6. PIE DE PÁGINA COMERCIAL ---
st.markdown(f"""
    <div class="sticky-footer-container">
        <p class="brand-line">powered by localmind.</p>
        <p><a href="https://wa.me/34602566673" target="_blank" class="footer-link">¿Quieres este asistente para tu negocio?</a></p>
    </div>
""", unsafe_allow_html=True)
