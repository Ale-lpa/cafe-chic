import streamlit as st
import json
from openai import OpenAI

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Café Chic | Powered by Localmind.",
    page_icon="🥑",
    layout="centered"
)

# --- 2. CLAVE SEGURA ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ Falta la clave API en los Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- 3. ESTILOS CSS (SINTONÍA TOTAL #6A8E7F) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* FONDO CON EL VERDE CORRECTO */
    [data-testid="stAppViewContainer"] {{
        background-color: #FFFFFF;
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #6A8E7F 25px, #6A8E7F 50px);
    }}
    
    [data-testid="stMainBlockContainer"] {{
        background-color: rgba(255, 255, 255, 0.98);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-width: 700px;
    }}

    /* BRANDING LOCALMIND */
    .branding-container {{ text-align: center; padding-bottom: 10px; }}
    .powered-by {{ color: #6A8E7F; font-size: 10px; letter-spacing: 3px; font-weight: bold; text-transform: uppercase; margin:0; }}
    .localmind-logo {{ color: #333; font-size: 18px; font-weight: 800; margin:0; font-family: sans-serif; }}
    .dot {{ color: #6A8E7F; }}

    .titulo-principal {{
        font-family: 'Dancing Script', cursive;
        color: #D4AF37;
        text-align: center;
        font-size: 3.5rem;
        margin-top: 0px;
    }}

    /* AJUSTE DE COLOR EN SUBTÍTULO */
    .subtitulo {{
        text-align: center;
        color: #6A8E7F;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 4px;
        font-size: 0.8rem;
        margin-bottom: 20px;
    }}

    /* OCULTAR ELEMENTOS NATIVOS */
    [data-testid="stHeader"], footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER BRANDING ---
st.markdown("""
<div class="branding-container">
    <p class="powered-by">Powered by</p>
    <p class="localmind-logo">Localmind<span class="dot">.</span></p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

# --- 5. BASE DE DATOS Y LÓGICA DE PEDIDOS (Igual al original) ---
MENU_DB = {
    "Tosta Aguacate": 8.50,
    "Huevos Benedictinos": 10.50,
    "Croissant Jamón": 5.50,
    "Bowl de Açaí": 9.00,
    "Café Latte": 2.50,
    "Cappuccino": 3.00,
    "Zumo Naranja": 3.50,
    "Mimosa": 6.00,
    "Tarta Zanahoria": 4.50,
    "Cheesecake": 5.00
}
menu_texto = ", ".join([f"{k} ({v}€)" for k,v in MENU_DB.items()])

if "pedido" not in st.session_state: st.session_state.pedido = []
if "pagado" not in st.session_state: st.session_state.pagado = False
if "mesa" not in st.session_state: st.session_state.mesa = "Mesa 5"

def agregar_item(nombre_plato):
    precio = MENU_DB.get(nombre_plato, 0.0)
    st.session_state.pedido.append({"item": nombre_plato, "precio": precio})
    st.session_state.pagado = False
    return f"[SYSTEM]: '{nombre_plato}' añadido. Responde al usuario en su idioma y ofrece venta cruzada."

# --- 6. SYSTEM PROMPT (ANTI-MEZCLA DE IDIOMAS) ---
system_prompt = f"""
Eres 'Leo', el camarero virtual premium de 'Café Chic'. 
MENÚ: {menu_texto}

REGLAS DE ORO (MÁXIMA PRIORIDAD):
1. **DETECTA EL IDIOMA:** Responde ÚNICA Y EXCLUSIVAMENTE en el idioma que el usuario utilice. 
2. **NO MEZCLES:** Está PROHIBIDO decir palabras en otros idiomas (ej. NO digas 'Bonjour' o 'Hi' si el usuario habla español). 
3. **TRADUCCIÓN:** Traduce los platos del menú al idioma del usuario (ej: 'Tosta Aguacate' -> 'Toast all'avocado' en italiano).
4. **VENTA CRUZADA:** Sugiere siempre un maridaje (bebida o postre).
"""

# --- 7. CHAT Y LÓGICA ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"]:
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

if prompt := st.chat_input("¿Qué te apetece tomar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Nota CTO: Usamos gpt-4o-mini para mayor velocidad y menor coste, manteniendo la calidad.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )
    
    full_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant", avatar="🥑"):
        st.markdown(full_response)
