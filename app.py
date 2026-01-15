import streamlit as st
import openai

# --- 1. IDENTIDAD CAFÉ CHIC ---
NOMBRE_RESTAURANTE = "Café<br>Chic" 
ESLOGAN = "ELEGANCIA EN CADA GRANO"
LOGO_URL = "" # Dejar vacío para evitar el recuadro de error

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Café Chic - LocalMind", layout="wide")

# --- 3. ESTÉTICA "LA BARCA" ADAPTADA ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    .stApp {{ background-image: url("https://i.postimg.cc/Dfs82Dv6/Gemini_Generated_Image_d7nq1bd7nq1bd7nq.png"); background-size: cover; background-attachment: fixed; }}
    .block-container {{ padding-top: 0rem !important; padding-bottom: 230px !important; max-width: 100% !important; }}
    [data-testid="stImage"] {{ background: transparent !important; }}
    [data-testid="stImage"] [data-testid="stMarkdownContainer"] {{ display: none !important; }}
    .stChatMessage [data-testid="stMarkdownContainer"] p {{ font-weight: 800; color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,1); }}
    .header-right-box {{ text-align: right; width: 100%; margin-top: -125px; padding-right: 20px; }}
    .restaurant-title {{ font-family: 'Playfair Display', serif; color: #002147; font-size: 60px; font-weight: 700; line-height: 0.85; margin: 0; }}
    .restaurant-subtitle {{ color: #C5A059; letter-spacing: 5px; font-size: 16px; font-weight: 900; border-top: 2px solid #002147; display: inline-block; margin-top: 5px; padding-top: 5px; text-transform: uppercase; }}
    .sticky-footer-container {{ position: fixed; left: 0; bottom: 115px; width: 100%; text-align: center; z-index: 100; }}
    .brand-line {{ color: #FFFFFF; font-weight: 900; font-size: 16px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
    .footer-link {{ color: #C5A059; text-decoration: none; font-weight: 900; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CABECERA ---
col_logo, col_text = st.columns([1, 3])
with col_text:
    st.markdown(f'<div class="header-right-box"><p class="restaurant-title">{NOMBRE_RESTAURANTE}</p><p class="restaurant-subtitle">{ESLOGAN}</p></div>', unsafe_allow_html=True)

# --- 5. LÓGICA CON ESCRITURA (STREAMING) ---
SYSTEM_PROMPT = f"Eres el barista y sumiller de {NOMBRE_RESTAURANTE}. Tu tono es sofisticado. Sugiere siempre maridajes entre café/té y repostería artesanal con sus precios."

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="☕" if m["role"]=="user" else "🍰"): st.markdown(m["content"])

if prompt := st.chat_input("¿Qué le apetece hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="☕"): st.markdown(prompt)
    with st.chat_message("assistant", avatar="🍰"):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        stream = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages, stream=True)
        full_res = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": full_res})

st.markdown(f'<div class="sticky-footer-container"><p class="brand-line">powered by localmind.</p><p><a href="https://wa.me/34602566673" target="_blank" class="footer-link">¿Quieres este asistente?</a></p></div>', unsafe_allow_html=True)
