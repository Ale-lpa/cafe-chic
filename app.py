import streamlit as st
import json
from openai import OpenAI

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Café Chic | Powered by Localmind.", page_icon="🥑", layout="centered")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error de conexión.")
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

    /* Forzar visibilidad de texto independientemente del tema del móvil */
    .stChatMessage p { color: #333333 !important; }
    [data-testid="stChatMessageAssistant"] p { color: #6A8E7F !important; font-weight: 600; }

    .branding-footer { text-align: center; padding-top: 40px; border-top: 1px solid #eee; margin-top: 30px; }
    .powered-by { color: #6A8E7F; font-size: 9px; letter-spacing: 3px; font-weight: bold; text-transform: uppercase; margin:0; }
    .localmind-logo { color: #333; font-size: 16px; font-weight: 800; margin:0; font-family: sans-serif; }
    .dot { color: #6A8E7F; }

    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS (Ground Truth) ---
MENU_DB = {
    "Desayunos": {"Bocadillo Jamón Ibérico": 6.00, "Croissant Croque Madame": 9.00, "Tosta con Aguacate Canarias": 5.90, "Tosta Tortilla Francesa": 5.80, "Huevos Benedictinos": 9.90, "Wrap César": 8.50},
    "Especialidades Canarias": {"Tapas Canarias para 2": 25.00, "Berenjenas fritas": 7.50, "Croquetas Jamón Ibérico": 11.00, "Huevos rotos (Chistorra o Gambas y Choco)": 3.90, "Queso Herreño asado": 11.50, "Papas Arrugadas": 6.50, "Ropas Vieja de Pulpo": 14.90, "Tacos de Bacalao": 14.90},
    "Ensaladas": {"Carpaccio de Mero": 15.90, "Ensalada Tibia de Langostinos": 14.90, "Ensalada de Burrata": 4.50, "Ensalada César": 12.50},
    "Pescados": {"Filete Lubina a la plancha": 7.50, "Brocheta de Mero a la parilla": 22.90, "Chipirones Saharianos": 17.50, "Paella de Mariscos": 24.00},
    "Postres": {"Crumble de Manzana": 6.00, "Milhojas de Vainilla": 5.00, "Profiteroles": 7.00, "Crepes Suzette": 5.00, "Bola de Helado": 2.50}
}

# --- 4. SYSTEM PROMPT REFORZADO ---
system_prompt = f"""
Eres 'Leo', el asistente experto de Café Chic. 
TU MENÚ: {json.dumps(MENU_DB)}

REGLAS DE ORO INNEGOCIABLES:
1. TRADUCCIÓN TOTAL: Si el usuario te habla en un idioma distinto al español, DEBES TRADUCIR TODO, incluidos los nombres de los platos y las categorías del menú en tus respuestas. Está prohibido listar el menú en español si te preguntan en otro idioma.
2. VENTA SUGERIDA OBLIGATORIA: En CADA respuesta que des, debes sugerir un maridaje. Si piden comida, sugiere una bebida (Zumo, Café, Vino). Si piden postre, sugiere un café. Hazlo con elegancia.
3. NUNCA digas que solo hablas español.
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
        res_placeholder = st.empty()
        full_res = ""
        stream = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                res_placeholder.markdown(full_res + "▌")
        res_placeholder.markdown(full_res)
    st.session_state.messages.append({"role": "assistant", "content": full_res})

st.markdown("""<div class="branding-footer"><p class="powered-by">Powered by</p><p class="localmind-logo">Localmind<span class="dot">.</span></p></div>""", unsafe_allow_html=True)
