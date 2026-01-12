import streamlit as st
import json
from openai import OpenAI

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Café Chic | Menú Inteligente", page_icon="🥑", layout="centered")

# --- 2. CLAVE SEGURA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error de conexión. Revisa los Secrets.")
    st.stop()

# --- 3. ESTILOS CSS (DISEÑO PREMIUM + BRANDING INFERIOR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Helvetica+Neue:wght@300;400;600&display=swap');

    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #6A8E7F 25px, #6A8E7F 50px);
    }
    
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.98);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-width: 700px;
    }

    .titulo-principal { font-family: 'Dancing Script', cursive; color: #D4AF37; text-align: center; font-size: 3.5rem; margin: 0; }
    .subtitulo { text-align: center; color: #6A8E7F; font-family: 'Helvetica Neue', sans-serif; letter-spacing: 4px; font-size: 0.8rem; margin-bottom: 20px; }

    /* BRANDING LOCALMIND AL FINAL */
    .branding-footer { text-align: center; padding-top: 40px; border-top: 1px solid #eee; margin-top: 30px; }
    .powered-by { color: #6A8E7F; font-size: 9px; letter-spacing: 3px; font-weight: bold; text-transform: uppercase; margin:0; }
    .localmind-logo { color: #333; font-size: 16px; font-weight: 800; margin:0; font-family: sans-serif; }
    .dot { color: #6A8E7F; }

    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. BASE DE DATOS COMPLETA (Actualizada con correcciones) ---
MENU_DB = {
    "Desayunos": {
        "Bocadillo Jamón Ibérico": 6.00, "Croissant Croque Madame": 9.00,
        "Tosta con Aguacate Canarias": 5.90, "Tosta Tortilla Francesa": 5.80,
        "Huevos Benedictinos": 9.90, "Wrap César": 8.50
    },
    "Especialidades Canarias": {
        "Tapas Canarias para 2": 25.00, "Berenjenas fritas": 7.50,
        "Croquetas Jamón Ibérico": 11.00, "Huevos rotos Chistorra/Gambas": 3.90, # CORREGIDO
        "Queso Herreño": 11.50, "Papas Arrugadas": 6.50,
        "Ropas Vieja de Pulpo": 14.90, "Tacos de Bacalao": 14.90
    },
    "Ensaladas": {
        "Carpaccio de Mero": 15.90, "Ensalada Tibia de Langostinos": 14.90,
        "Ensalada de Burrata": 14.50, "Ensalada César": 12.50
    },
    "Poke Bowls": { "Poke de Salmón": 14.50, "Poke de Pollo Crujiente": 13.50 },
    "Pescados": { 
        "Filete Lubina": 7.50, # CORREGIDO 
        "Brocheta de Mero": 22.90, "Chipirones Saharianos": 17.50, "Paella de Mariscos": 24.00 
    },
    "Carnes": { "Solomillo de Vaca Angus": 23.90, "Pollo Yassa": 14.90, "Secreto Ibérico": 17.90, "Gulash Húngaro": 16.50 },
    "Crepes de Harina de Sarraceno": { "La Bretoña": 11.90, "La Vegetariana": 12.90, "La Salchicha": 13.90 },
    "Vegetal": { "Humus de Alubia Carillas": 9.90, "Espaguetis de Calabacín": 13.50, "Arroz Coreano": 12.90 },
    "Postres": { "Crumble de Manzana": 6.00, "Milhojas de Vainilla": 5.00, "Profiteroles": 7.00, "Crepes Suzette": 5.00, "Bola de Helado": 2.50 }
}

# --- 5. LÓGICA DE SYSTEM PROMPT ---
system_prompt = f"""
Eres 'Leo', el asistente experto de Café Chic. 
TU MENÚ REAL COMPLETO ES: {json.dumps(MENU_DB)}

REGLAS CRÍTICAS:
1. IDIOMA: Responde SIEMPRE en el idioma del cliente. Si te hablan en inglés, responde en inglés. Prohibido decir que solo hablas español.
2. PRECIOS: Respeta estrictamente los precios de la base de datos.
3. CONOCIMIENTO: Conoces todas las secciones: Desayunos, Especialidades, Ensaladas, Pokes, Pescados, Carnes, Crepes de Sarraceno, Vegetal y Postres.
4. NO INVENTES: Si algo no está en el menú, no existe.
"""

# --- 6. INTERFAZ ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

if prompt := st.chat_input("Consulta nuestra carta completa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)

    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages)
    ai_msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
    with st.chat_message("assistant", avatar="🥑"): st.markdown(ai_msg)

# --- 7. BRANDING LOCALMIND AL FINAL ---
st.markdown("""
<div class="branding-footer">
    <p class="powered-by">Powered by</p>
    <p class="localmind-logo">Localmind<span class="dot">.</span></p>
</div>
""", unsafe_allow_html=True)
