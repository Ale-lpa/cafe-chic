import streamlit as st
from openai import OpenAI

# 1. Configuración de página (Poner antes de cualquier otro comando)
st.set_page_config(page_title="Café Chic - AI Assistant", page_icon="☕", layout="centered")

# 2. Estilo CSS "Localmind Premium" (Negro absoluto y Azul Eléctrico)
st.markdown("""
    <style>
    /* Fondo negro absoluto */
    .stApp {
        background-color: #000000;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedor del branding Localmind. */
    .branding-container {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #001A84;
        margin-bottom: 30px;
    }
    .powered-by {
        color: #001A84;
        font-size: 12px;
        letter-spacing: 3px;
        font-weight: bold;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .localmind-logo {
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }
    .dot { color: #001A84; }

    /* Mensajes del Chat */
    [data-testid="stChatMessage"] {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 15px;
        margin-bottom: 10px;
    }

    /* Estilo del input */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* Títulos y textos */
    h1, h2, p {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Cabecera Visual
st.markdown("""
    <div class="branding-container">
        <p class="powered-by">Powered by</p>
        <p class="localmind-logo">Localmind<span class="dot">.</span></p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>Bienvenido a Café Chic</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Tu asistente inteligente para una experiencia gourmet.</p>", unsafe_allow_html=True)

# 4. Lógica del Cerebro (System Prompt - SIN PEDIDOS)
# IMPORTANTE: Pon tu clave de OpenAI en los Secrets de Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "Eres el asistente oficial de Café Chic. Tu tono es elegante, amable y profesional. "
            "Tu misión es informar sobre nuestra carta de cafés de especialidad, repostería artesanal y horarios. "
            "REGLA CRÍTICA: No puedes tomar pedidos, gestionar carritos ni procesar pagos. "
            "Si el cliente quiere pedir algo, di: 'Para garantizar la mejor calidad, los pedidos se realizan "
            "directamente en nuestro mostrador. Estaré encantado de ayudarte a elegir la mejor opción antes de que pidas'."
            "Menciona que Café Chic es un lugar diseñado para el disfrute del buen café."
        )}
    ]

# 5. Chat Interface
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o-mini", # O el que estés usando
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
