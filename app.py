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

# --- ESTILOS CSS (DISEÑO COMPACTO Y CHIC) ---
st.markdown("""
    <style>
    /* IMPORTAR TIPOGRAFÍA */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO PRINCIPAL CON RAYAS (Igual que antes) */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
        background-image: repeating-linear-gradient(
            90deg,
            #FFFFFF,
            #FFFFFF 25px,
            #8FA891 25px,
            #8FA891 50px
        );
    }
    
    /* 2. CONTENEDOR PRINCIPAL (MÁS COMPACTO) */
    /* Reducimos padding para aprovechar espacio */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.96);
        padding: 15px; /* Antes 30px, ahora más ajustado */
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-top: 10px;
        margin-bottom: 10px;
        border: 2px solid #D4AF37;
        max-width: 700px;
    }

    /* 3. BARRA LATERAL */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 2px solid #D4AF37;
    }
    section[data-testid="stSidebar"] h1 {
        color: #D4AF37 !important;
        font-family: 'Dancing Script', cursive !important;
        font-size: 2rem !important; /* Un poco más pequeño */
        margin-bottom: 0px;
    }
    section[data-testid="stSidebar"] p, .stAlert {
        color: #556B2F !important;
        background-color: #F9FBF9 !important;
        border: 1px solid #8FA891 !important;
        font-size: 0.9rem;
    }
    
    /* 4. TÍTULOS (Más pegados) */
    .titulo-principal {
        font-family: 'Dancing Script', cursive;
        color: #D4AF37;
        text-align: center;
        font-size: 3rem; /* Reducido un poco */
        margin-top: 0px;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .subtitulo {
        text-align: center;
        color: #8FA891;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 15px; /* Menos espacio debajo */
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* 5. BURBUJAS DE CHAT (COMPACTAS) */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 10px 15px; /* Menos relleno interno */
        margin-bottom: 8px; /* Menos espacio entre mensajes */
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Estilos específicos burbujas */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid #8FA891;
        background-color: #F8FAF8;
    }
    .stChatMessage .stAvatar {
        background-color: #8FA891 !important;
        color: white !important;
        width: 28px; /* Avatar más pequeño */
        height: 28px;
    }

    /* 6. TEXTO DE LOS MENSAJES */
    .stChatMessage p {
        color: #333 !important;
        font-size: 0.95rem;
        line-height: 1.4; /* Líneas más juntas */
        margin-bottom: 0px;
    }
    /* Precios y Platos destacados */
    .stChatMessage strong {
        color: #D4AF37 !important;
        font-weight: 700;
    }

    /* 7. OCULTAR ELEMENTOS */
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

menu_data = cargar_menu()
menu_texto = json.dumps(menu_data, ensure_ascii=False)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1>Café Chic</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #8FA891 !important; margin-top:-10px;'>RESTAURANTE & BRUNCH</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**🕒 Horario**")
    st.success("""
    L-X: 10-16h | J-V: 10-23h
    Sáb: 11-17h | Dom: CERRADO
    """)
    
    st.markdown("**📞 Reservas**")
    st.info("682 27 26 51")
    st.caption("📍 C/ Mendizábal, 39 - Vegueta")

# --- CHAT ---
# Aquí cambiamos las instrucciones para asegurar EUROS y DESCIPCIONES
system_prompt = f"""
Eres el asistente virtual de 'Café Chic'.
Estilo: Fresco, profesional y persuasivo. Emojis: 🥑, 🌿, ☕, 🥂.
MENÚ: {menu_texto}

REGLAS DE FORMATO (ESTRICTAS):
1. **MONEDA:** Usa SIEMPRE el símbolo de Euro (€) al final del precio. NUNCA uses dólares ($).
2. **ESTRUCTURA DE PLATO:** Cuando recomiendes, usa este formato compacto:
   - **Nombre del Plato** (Precio €)
   - *Pequeña descripción atractiva basada en los ingredientes.*
3. **ESPACIADO:** No dejes líneas en blanco innecesarias. Agrupa la información.
4. **VENTA CRUZADA:** Si piden comida, sugiere bebida corta y directa.

EJEMPLO DE RESPUESTA IDEAL:
"Te recomiendo los **Huevos Benedictinos** (9,90€). Son deliciosos huevos escalfados sobre pan tostado con bacon crujiente y nuestra salsa holandesa casera 🍳.
¿Te apetece acompañarlos con una **Mimosa** (5,50€) bien fresquita? 🥂"
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "¡Hola! 🌿 Bienvenido a **Café Chic**.\n\n¿Te apetece un **Brunch** completo 🥑 o prefieres ver opciones de almuerzo? ✨"}
    ]

# Títulos
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

# Renderizar chat
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

# Input usuario
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
