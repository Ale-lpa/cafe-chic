import streamlit as st
import json
from openai import OpenAI

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Café Chic | Virtual Assistant", page_icon="🥑", layout="centered")

# --- CLAVE SEGURA ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ Falta la clave API en los Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {background-color: #FFFFFF;}
    section[data-testid="stSidebar"] {background-color: #EBF2EB; border-right: 2px solid #8FA891;}
    .titulo-principal {font-family: 'Helvetica Neue', sans-serif; color: #556B2F; text-align: center; font-size: 3rem; margin-top: 10px; text-transform: uppercase;}
    .subtitulo {text-align: center; color: #D4AF37; font-weight: 600; font-size: 1rem; margin-bottom: 30px; letter-spacing: 2px; text-transform: uppercase;}
    .stChatMessage {background-color: #FFFFFF; border-radius: 15px; border: 1px solid #E0E0E0;}
    .stChatMessage .stAvatar {background-color: #8FA891 !important; color: white !important;}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- DATOS ---
@st.cache_data
def cargar_menu():
    try:
        with open('menu_maestro.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

menu_texto = json.dumps(cargar_menu(), ensure_ascii=False)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #556B2F;'>🌿 Café Chic</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.success("**Lun-Mié:** 10-16h\n**Jue-Vie:** 10-23h\n**Sáb:** 11-17h\n**Dom:** CERRADO")
    st.info("📞 **682 27 26 51**")

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "¡Hola! 🌿 Bienvenido a **Café Chic**. ¿Te apetece un Brunch o vienes a almorzar? 🥑"}]

st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Brunch • Lunch • Cocktails</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
        st.write(m["content"])

if prompt := st.chat_input("¿Qué me recomiendas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)
    
    with st.chat_message("assistant", avatar="🥑"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"Eres el asistente de Café Chic. MENÚ: {menu_texto}"}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
