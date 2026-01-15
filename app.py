import streamlit as st
import openai

# --- 1. CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_RESTAURANTE = "Nombre de<br>Tu Local" 
ESLOGAN = "EXPERIENCIA GASTRONÓMICA"
# Imagen de fondo: Restaurante de lujo
FONDO_URL = "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=2070&auto=format&fit=crop"
LOGO_URL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" 

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LocalMind AI", layout="wide")

# --- 3. ESTÉTICA PROFESIONAL PULIDA ---
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
    
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.3);
        z-index: -1;
    }}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 250px !important;
        max-width: 100% !important;
    }}

    /* Limpieza de errores de imagen */
    [data-testid="stImage"] {{ background: transparent !important; }}
    [data-testid="stImage"] div {{ display: none !important; }}

    /* Estilo de los mensajes */
    .stChatMessage [data-testid="stMarkdownContainer"] p {{
        font-weight: 800 !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8); 
    }}

    /* Cabecera */
    .logo-container {{ position: absolute; left: 15px; top: 35px; z-index: 100; }}
    .header-right-box {{
        text-align: right; width: 100%;
        margin-top: -125px; padding-right: 20px;
    }}
    .restaurant-title {{
        font-family: 'Playfair Display', serif;
        color: #FFFFFF;
        font-size: 55px; font-weight: 700;
        line-height: 0.85; margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    }}
    .restaurant-subtitle {{
        color: #C5A059;
        letter-spacing: 5px; font-size: 14px;
        font-weight: 900 !important;
        border-top: 2px solid #C5A059;
        display: inline-block;
        margin-top: 8px; padding-top: 5px;
        text-transform: uppercase;
    }}

    /* --- LIMPIEZA TOTAL DEL CUADRO DE TEXTO --- */
    [data-testid="stChatInput"] {{
        border: none !important; 
        box-shadow: none !important;
        border-radius: 10px !important;
        background-color: rgba(0, 33, 71, 0.8) !important; /* Azul LocalMind */
        color: white !important;
    }}
    
    /* Eliminar la raya superior que pone Streamlit por defecto */
    .stChatInputContainer {{
        background-color: transparent !important;
        border-top: none !important;
        padding-bottom: 35px !important;
        bottom: 30px !important;
    }}

    /* Footer LocalMind */
    .sticky-footer-container {{
        position: fixed; left: 0; bottom: 125px; width: 100%; text-align: center; z-index: 100;
        background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
        padding-bottom: 10px;
    }}
    .brand-line {{ color: #FFFFFF !important; font-weight: 900; font-size: 15px; text-shadow: 2px 2px 4px #000; margin: 0; }}
    .footer-link {{ color: #C5A059 !important; text-decoration: none; font-weight: 900; font-size: 14px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CABECERA ---
st.markdown('<div class="logo-container"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="header-right-box"><p class="restaurant-title">{NOMBRE_RESTAURANTE}</p><p class="restaurant-subtitle">{ESLOGAN}</p></div>', unsafe_allow_html=True)

# --- 5. LÓGICA DE ASISTENTE CON ICONOS NUEVOS ---
# Sombrero de copa (🎩) y Cara sonriente (😊)
SYSTEM_PROMPT = f"Eres el sumiller virtual de {NOMBRE_RESTAURANTE}. Ofrece precios, vinos y maridajes de forma experta. Powered by LocalMind."

if "messages" not in st.session_state: st.session_state.messages = []

# Dibujar historial con nuevos emoticonos
for message in st.session_state.messages:
    icon = "😊" if message["role"] == "user" else "🎩"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("Escriba su consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="😊"): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎩"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        stream = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages, 
            stream=True
        )
        full_response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- 6. PIE DE PÁGINA ---
st.markdown(f"""
    <div class="sticky-footer-container">
        <p class="brand-line">powered by localmind.</p>
        <p><a href="https://wa.me/34602566673" target="_blank" class="footer-link">¿Deseas este asistente en tu restaurante?</a></p>
    </div>
""", unsafe_allow_html=True)
