import streamlit as st
from openai import OpenAI

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Café Chic | Powered by Localmind",
    page_icon="☕",
    layout="centered"
)

# --- 2. CLAVE SEGURA ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ Falta la clave API en los Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- 3. ESTILOS CSS (DISEÑO PREMIUM LOCALMIND) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* FONDO Y CONTENEDOR */
    [data-testid="stAppViewContainer"] {
        background-color: #000000; /* Fondo negro para que resalte el azul Localmind */
    }
    
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(0, 0, 0, 0.9);
        border: 1px solid #001A84;
        border-radius: 20px;
        padding: 25px;
        max-width: 700px;
    }

    /* BRANDING LOCALMIND */
    .branding-container {
        text-align: center;
        padding-bottom: 10px;
    }
    .powered-by {
        color: #001A84;
        font-size: 11px;
        letter-spacing: 3px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    .localmind-logo {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        margin-top: -10px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .dot { color: #001A84; }

    /* TÍTULO LOCAL */
    .titulo-local {
        font-family: 'Dancing Script', cursive;
        color: #ffffff;
        text-align: center;
        font-size: 3.5rem;
        margin-top: 10px;
    }

    /* CHAT */
    .stChatMessage {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 15px;
    }
    
    p, span, div {
        color: #ffffff !important;
    }

    /* OCULTAR ELEMENTOS INNECESARIOS */
    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. CABECERA DE MARCA ---
st.markdown("""
    <div class="branding-container">
        <p class="powered-by">Powered by</p>
        <p class="localmind-logo">Localmind<span class="dot">.</span></p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-local">Café Chic</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #001A84 !important; font-weight: bold; letter-spacing: 2px;'>ASISTENTE VIRTUAL</p>", unsafe_allow_html=True)

# --- 5. BASE DE DATOS DEL MENÚ (Solo para consulta) ---
menu_info = """
- Tosta Aguacate (8.50€)
- Huevos Benedictinos (10.50€)
- Croissant Jamón (5.50€)
- Bowl de Açaí (9.00€)
- Café Latte (2.50€)
- Cappuccino (3.00€)
- Zumo Naranja (3.50€)
- Mimosa (6.00€)
- Tarta Zanahoria (4.50€)
- Cheesecake (5.00€)
"""

# --- 6. CHATBOT (CEREBRO SIN PEDIDOS) ---
system_prompt = f"""
Eres 'Leo', el asistente experto de 'Café Chic', impulsado por la tecnología de Localmind. 

TU MISIÓN:
1. Informar sobre nuestra carta de cafés, brunch y repostería artesanal.
2. Ayudar a los clientes con dudas sobre alérgenos o sugerencias según sus gustos.
3. Ser elegante, amable y profesional.

REGLAS CRÍTICAS:
- NO puedes realizar pedidos ni gestionar tickets de compra.
- Si el cliente quiere pedir algo, di: 'Para ofrecerte la mejor experiencia, los pedidos se realizan directamente en el mostrador con nuestro equipo. ¡Te esperamos!'.
- Los nombres del menú son: {menu_info}
- Detecta el idioma del cliente y responde en su idioma, pero siempre mencionando la calidad de Café Chic.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Mostrar historial
for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"]:
        with st.chat_message(m["role"], avatar="☕" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

# Entrada de usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy en Café Chic?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="☕"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
