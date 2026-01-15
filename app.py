import streamlit as st
import openai

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_LOCAL = "Café<br>Chic" 
ESLOGAN = "EL ARTE DE LA PAUSA"

st.set_page_config(page_title="Café Chic - LocalMind", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&display=swap');
    
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.5), rgba(255,255,255,0.5)), 
                          url("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&q=80");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    .block-container {{ padding-top: 0rem !important; padding-bottom: 230px !important; max-width: 100% !important; }}

    /* TEXTO DEL CHAT: MARRÓN CAFÉ SOBRE BLANCO */
    .stChatMessage [data-testid="stMarkdownContainer"] p {{
        font-weight: 700 !important;
        color: #3E2723 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 1px rgba(255,255,255,0.8); 
    }}

    .header-right-box {{
        text-align: right; width: 100%; margin-top: -110px; padding-right: 25px;
    }}

    .restaurant-title {{
        font-family: 'Playfair Display', serif;
        color: #4E342E; /* Café intenso */
        font-size: 65px; 
        font-weight: 700;
        font-style: italic;
        line-height: 0.8;
        margin: 0;
    }}
    
    .restaurant-subtitle {{
        color: #8D6E63;
        letter-spacing: 7px;
        font-size: 14px;
        font-weight: 900;
        border-top: 1px solid #4E342E;
        display: inline-block;
        margin-top: 10px;
        padding-top: 5px;
        text-transform: uppercase;
    }}

    .sticky-footer-container {{
        position: fixed; left: 0; bottom: 110px; width: 100%; text-align: center; z-index: 100;
        background: linear-gradient(to top, rgba(255,248,225,0.8) 0%, rgba(255,248,225,0) 100%);
        padding-bottom: 10px;
    }}

    .brand-line {{ color: #4E342E !important; font-weight: 900; font-size: 16px; }}
    .footer-link {{ color: #A1887F !important; text-decoration: none; font-weight: 900; }}
    </style>
""", unsafe_allow_html=True)

# CABECERA
st.markdown(f'<div class="header-right-box"><p class="restaurant-title">{NOMBRE_LOCAL}</p><p class="restaurant-subtitle">{ESLOGAN}</p></div>', unsafe_allow_html=True)

# LÓGICA DE ASISTENTE
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🥐" if m["role"]=="user" else "☕"): st.markdown(m["content"])

if prompt := st.chat_input("Desea un café de especialidad..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🥐"): st.markdown(prompt)
    with st.chat_message("assistant", avatar="☕"):
        contexto = [{"role": "system", "content": "Eres el barista sumiller de Café Chic. Tu tono es refinado y parisino. Sugiere maridajes de café de especialidad con repostería fina indicando precios."}] + st.session_state.messages
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        stream = client.chat.completions.create(model="gpt-4o", messages=contexto, stream=True)
        full_res = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": full_res})

st.markdown(f'<div class="sticky-footer-container"><p class="brand-line">powered by localmind.</p><p><a href="https://wa.me/34602566673" target="_blank" class="footer-link">¿Quieres este asistente para tu café?</a></p></div>', unsafe_allow_html=True)
