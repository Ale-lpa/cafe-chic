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

# --- ESTILOS CSS (DISEÑO PULIDO Y TEXTO CUADRADO) ---
st.markdown("""
    <style>
    /* IMPORTAR TIPOGRAFÍA */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO PRINCIPAL CON RAYAS */
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
    
    /* 2. CONTENEDOR PRINCIPAL */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.98); /* Más opaco para leer mejor */
        padding: 25px; /* Más espacio interno */
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin-top: 20px;
        margin-bottom: 20px;
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
        font-size: 2.2rem !important;
        margin-bottom: 5px;
    }
    section[data-testid="stSidebar"] p, .stAlert {
        color: #556B2F !important;
        background-color: #F9FBF9 !important;
        border: 1px solid #8FA891 !important;
        font-size: 0.9rem;
    }
    
    /* 4. TÍTULOS */
    .titulo-principal {
        font-family: 'Dancing Script', cursive;
        color: #D4AF37;
        text-align: center;
        font-size: 3.5rem;
        margin-top: 0px;
        margin-bottom: 5px;
        line-height: 1.2;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.1);
    }
    .subtitulo {
        text-align: center;
        color: #8FA891;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 25px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* 5. BURBUJAS DE CHAT (AQUÍ ESTÁ EL AJUSTE CLAVE) */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 18px; /* Bordes más redondeados */
        padding: 20px 25px; /* MÁS AIRE: Texto perfectamente encuadrado */
        margin-bottom: 15px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    /* Burbuja del Asistente */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid #8FA891; /* Borde lateral verde más visible */
        background-color: #FDFDFD;
    }
    
    /* Avatar */
    .stChatMessage .stAvatar {
        background-color: #8FA891 !important;
        color: white !important;
        width: 35px;
        height: 35px;
    }

    /* 6. TEXTO DE LOS MENSAJES (LEIBILIDAD) */
    .stChatMessage p, .stChatMessage li {
        color: #444 !important;
        font-size: 1.05rem; /* Letra un pelín más grande */
        line-height: 1.6; /* MÁS INTERLINEADO: Para que no se vea pegado */
        margin-bottom: 8px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Precios destacados */
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

# --- CHAT (CEREBRO POLÍGLOTA & EXPERTO EN VENTAS) ---
system_prompt = f"""
Eres el asistente virtual de 'Café Chic'.
Estilo: Fresco, profesional, "aesthetic" y persuasivo. Emojis: 🥑, 🌿, ☕, 🥂.
MENÚ: {menu_texto}

🌍 REGLAS DE IDIOMA (IMPORTANTE):
1. **AUTO-DETECTAR:** Responde SIEMPRE en el mismo idioma que use el cliente.
   - Si escribe en Inglés 🇬🇧 -> Responde en Inglés (y traduce los platos/descripciones).
   - Si escribe en Alemán 🇩🇪 -> Responde en Alemán.
   - Si escribe en Italiano 🇮🇹 -> Responde en Italiano.
2. **EXPLICACIÓN CULINARIA:** Si el cliente es extranjero, explica los ingredientes locales (ej: explica qué es el "Mojo" o el "Gofio" si aparece).

💰 REGLAS DE FORMATO:
1. **MONEDA:** Usa SIEMPRE el símbolo de Euro (€) al final del precio.
2. **ESTRUCTURA DE PLATO:**
   - **Nombre del Plato** (Precio €)
   - *Breve descripción deliciosa.*
3. **VENTA CRUZADA:** Sugiere siempre bebida con comida y postre con café.

EJEMPLO DE RESPUESTA (INGLÉS):
"I recommend the **Huevos Benedictinos** (9,90€). Delicious poached eggs on toasted bread with crispy bacon and our homemade hollandaise sauce 🍳.
Would you like to pair it with a fresh **Mimosa** (5,50€)? 🥂"
"""
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
