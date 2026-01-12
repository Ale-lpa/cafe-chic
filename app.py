import streamlit as st
import json
from openai import OpenAI

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Café Chic | Powered by Localmind.", page_icon="🥑", layout="centered")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error de conexión. Revisa los Secrets.")
    st.stop()

# --- 2. CSS ANTI-MODO OSCURO Y ALTO CONTRASTE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Helvetica+Neue:wght@300;400;600&display=swap');

    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #6A8E7F 25px, #6A8E7F 50px) !important;
    }
    
    [data-testid="stMainBlockContainer"] {
        background-color: white !important;
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    .titulo-principal { font-family: 'Dancing Script', cursive; color: #D4AF37; text-align: center; font-size: 3.5rem; margin: 0; }
    .subtitulo { text-align: center; color: #6A8E7F; font-family: 'Helvetica Neue', sans-serif; letter-spacing: 4px; font-size: 0.8rem; margin-bottom: 20px; }

    /* Forzar visibilidad de texto */
    .stChatMessage p { color: #333333 !important; }
    [data-testid="stChatMessageAssistant"] p { color: #6A8E7F !important; font-weight: 600; }

    .branding-footer { text-align: center; padding-top: 40px; border-top: 1px solid #eee; margin-top: 30px; }
    .powered-by { color: #6A8E7F; font-size: 9px; letter-spacing: 3px; font-weight: bold; text-transform: uppercase; margin:0; }
    .localmind-logo { color: #333; font-size: 16px; font-weight: 800; margin:0; font-family: sans-serif; }
    .dot { color: #6A8E7F; }

    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS REAL (Ground Truth) ---
MENU_DB = {
    "Desayunos": {"Bocadillo Jamón Ibérico": 6.00, "Croissant Croque Madame": 9.00, "Tosta con Aguacate Canarias": 5.90, "Tosta Tortilla Francesa": 5.80, "Huevos Benedictinos": 9.90, "Wrap César": 8.50},
    "Especialidades Canarias": {"Tapas Canarias para 2": 25.00, "Berenjenas fritas": 7.50, "Croquetas Jamón Ibérico": 11.00, "Huevos rotos (Chistorra o Gambas y Choco)": 3.90, "Queso Herreño asado": 11.50, "Papas Arrugadas": 6.50, "Ropas Vieja de Pulpo": 14.90, "Tacos de Bacalao": 14.90},
    "Ensaladas": {"Carpaccio de Mero": 15.90, "Ensalada Tibia de Langostinos": 14.90, "Ensalada de Burrata": 14.50, "Ensalada César": 12.50},
    "Pescados": {"Filete Lubina a la plancha": 7.50, "Brocheta de Mero a la parilla": 22.90, "Chipirones Saharianos": 17.50, "Paella de Mariscos": 24.00},
    "Carnes": {"Solomillo de Vaca Angus": 23.90, "Pollo Yassa": 14.90, "Secreto Ibérico": 17.90, "Gulash Húngaro": 16.50},
    "Crepes de Harina de Sarraceno": {"La Bretoña": 11.90, "La Vegetariana": 12.90, "La Salchicha": 13.90},
    "Vegetal": {"Humus de Alubia Carillas": 9.90, "Espaguetis de Calabacín": 13.50, "Arroz Coreano": 12.90},
    "Postres": {"Crumble de Manzana": 6.00, "Milhojas de Vainilla": 5.00, "Profiteroles": 7.00, "Crepes Suzette": 5.00, "Bola de Helado": 2.50}
}

# --- 4. SYSTEM PROMPT (REGLA DEL € BLINDADA) ---
system_prompt = f"""
Eres 'Leo', el asistente experto de Café Chic. 
TU MENÚ REAL: {json.dumps(MENU_DB)}

REGLAS DE ORO:
1. TRADUCCIÓN OBLIGATORIA: Si te hablan en otro idioma, traduce TODO el menú.
2. SÍMBOLO DEL EURO: Muestra SIEMPRE el símbolo '€' junto a cada precio (Ej: 5.90€). Nunca pongas el número solo.
3. VENTA SUGERIDA: Sugiere siempre acompañar con un 'Zumo de Naranja Natural'. Indica que las sugerencias pueden cambiar diariamente.
4. NO INVENTES: Si algo no está en el menú, no existe.
"""

# --- 5. INTERFAZ ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "☕"):
            st.markdown(m["content"])

if prompt := st.chat_input("Consulta nuestra carta completa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="☕"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="🥑"):
        res_placeholder =
