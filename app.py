import streamlit as st
import json
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Café Chic | Asistente Virtual",
    page_icon="🥑",
    layout="centered"
)

# --- CLAVE SEGURA ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ Falta la clave API en los Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- ESTILOS CSS (ESTILO TARJETA DE VISITA: RAYAS Y DORADO) ---
st.markdown("""
    <style>
    /* IMPORTAR TIPOGRAFÍA CURSIVA ELEGANTE */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO PRINCIPAL CON RAYAS VERTICALES (Como la tarjeta) */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF; /* Color base */
        background-image: repeating-linear-gradient(
            90deg,
            #FFFFFF,
            #FFFFFF 25px,
            #8FA891 25px, /* Verde Salvia de la tarjeta */
            #8FA891 50px
        );
    }
    
    /* Contenedor principal para centrar y dar fondo blanco al chat */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.95); /* Blanco casi opaco */
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px;
        margin-bottom: 20px;
        border: 2px solid #D4AF37; /* Borde dorado fino */
    }

    /* 2. BARRA LATERAL (Blanca limpia, como la cabecera de la tarjeta) */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 2px solid #D4AF37; /* Separador dorado */
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    /* Textos de la barra lateral */
    section[data-testid="stSidebar"] h1 {
        color: #D4AF37 !important; /* Título dorado */
        font-family: 'Dancing Script', cursive !important;
        font-size: 2.5rem !important;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] div, .stAlert {
        color: #556B2F !important; /* Texto verde oscuro */
        font-family: 'Helvetica Neue', sans-serif;
        background-color: #F9FBF9 !important; /* Fondo muy clarito para las cajas */
        border: 1px solid #8FA891 !important;
    }
    
    /* 3. TÍTULOS PRINCIPALES (Estilo Logo Dorado) */
    .titulo-principal {
        font-family: 'Dancing Script', cursive; /* Tipografía de logo */
        color: #D4AF37; /* Dorado */
        text-align: center;
        font-size: 4rem;
        margin-top: 0px;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .subtitulo {
        text-align: center;
        color: #8FA891; /* Verde Salvia */
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 30px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* 4. BURBUJAS DE CHAT (Limpias y Chic) */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    /* Burbuja del Asistente */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border: 1px solid #8FA891; /* Borde verde suave */
        background-color: #F4F8F4; /* Fondo verde muy pálido */
    }
    /* Avatar del asistente */
    .stChatMessage .stAvatar {
        background-color: #8FA891 !important; /* Verde Salvia */
        color: white !important;
    }
    /* Avatar del usuario */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) .stAvatar {
        background-color: #D4AF37 !important; /* Dorado */
    }

    /* 5. TEXTOS Y DETALLES */
    .stChatMessage p {
        color: #444 !important;
        font-size: 1.05rem;
        line-height: 1.5;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stChatMessage strong {
        color: #D4AF37 !important; /* Platos en Dorado */
    }
    
    /* 6. BARRA DE ENTRADA DE TEXTO */
    [data-testid="stChatInput"] {
        border-color: #D4AF37 !important; /* Borde dorado */
        border-radius: 25px;
    }

    /* 7. OCULTAR ELEMENTOS INNECESARIOS */
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- DATOS ---
@st.cache_data
def cargar_menu():
    try:
        with open('menu_maestro.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

menu_data = cargar_menu()
menu_texto = json.dumps(menu_data, ensure_ascii=False)

# --- BARRA LATERAL (ESTILO LOGO) ---
with st.sidebar:
    # Usamos la tipografía cursiva para el título
    st.markdown("<h1>Café Chic</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9rem; margin-top:-15px; color: #8FA891 !important;'>RESTAURANTE & BRUNCH</p>", unsafe_allow_html=True)
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
    st.caption("📍 C/ Mendizábal, 39 - Vegueta")

# --- CHAT ---
system_prompt = f"""
Eres el asistente virtual de 'Café Chic'.
Estilo: Fresco, amable y elegante. Usas emojis como 🥑, 🌿, ☕, 🥂.
MENÚ: {menu_texto}

REGLAS:
1. Horarios: L-X cierre 16:00. J-V cierre 23:00. Domingo Cerrado.
2. Venta Cruzada: Sugiere bebida con comida y postre con café.
3. Sé conciso y visualmente atractivo.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "¡Hola! 🌿 Bienvenido a **Café Chic**.\n\n¿Te apetece un **Brunch** delicioso 🥑 o vienes a disfrutar de nuestro almuerzo? 🥂"}
    ]

# Títulos principales con el nuevo estilo
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

if prompt := st.chat_input("Ej: ¿Qué lleva la Tosta con Aguacate?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🥑"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
