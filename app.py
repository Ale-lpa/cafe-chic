import streamlit as st
import json
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Café Chic | Virtual Assistant",
    page_icon="🥑",
    layout="centered"
)

# --- 1. TU CLAVE DE OPENAI (MODO SEGURO) ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ No se ha encontrado la clave API. Por favor, configúrala en los 'Secrets'.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- 2. ESTILOS CSS (DISEÑO SAGE GREEN & GOLD) ---
st.markdown("""
    <style>
    /* 1. FONDO PRINCIPAL: Blanco Puro */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }

    /* 2. BARRA LATERAL (VERDE SALVIA CHIC) */
    section[data-testid="stSidebar"] {
        background-color: #EBF2EB;
        border-right: 2px solid #8FA891;
    }
    section[data-testid="stSidebar"] h1 { color: #556B2F !important; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] div { color: #4A5D4B !important; }
    
    /* 3. TÍTULOS */
    .titulo-principal {
        font-family: 'Helvetica Neue', sans-serif;
        color: #556B2F;
        text-align: center;
        font-size: 3.5rem;
        font-weight: 300;
        margin-top: 20px;
        text-transform: uppercase;
    }
    .subtitulo {
        text-align: center;
        color: #D4AF37;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    /* 4. CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #E0E0E0;
    }
    .stChatMessage p { color: #444 !important; }
    .stChatMessage strong { color: #D4AF37 !important; }
    .stChatMessage .stAvatar { background-color: #8FA891 !important; color: white !important; }

    /* 5. LIMPIEZA */
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CARGAR DATOS ---
@st.cache_data
def cargar_menu():
    try:
        with open('menu_maestro.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError: return []

menu_data = cargar_menu()
menu_texto = json.dumps(menu_data, ensure_ascii=False)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿 Café Chic</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; margin-top:0px;'>LAS PALMAS</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🕒 Horario")
    st.success("""
    **Lun - Mié:** 10:00 - 16:00
    **Jue - Vie:** 10:00 - 23:00
    **Sábado:** 11:00 - 17:00
    **Domingo:** CERRADO
    """)
    
    st.markdown("### 📞 Reservas")
    st.info("**682 27 26 51**")
    st.markdown("---")

# --- 5. LÓGICA DEL CHAT ---
system_prompt = f"""
Eres el asistente virtual de 'Café Chic'. Estilo: Fresco, natural y "chic".
MENÚ: {menu_texto}
REGLAS:
1. Horarios: L-X cierre 16:00. J-V cierre 23:00. Domingo Cerrado.
2. Venta Cruzada: Sugiere bebida con comida.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "¡Hola! 🌿 Bienvenido a **Café Chic**.\n\n¿Te apetece un buen desayuno/brunch o vienes a por el almuerzo? 🥑"}
    ]

st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Brunch • Lunch • Cocktails</div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🥑" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

if prompt := st.chat_input("Ej: ¿Qué lleva la Tosta con Aguacate?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🥑"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
