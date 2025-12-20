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

# --- ESTILOS CSS (DISEÑO CHIC, RAYAS Y DORADO) ---
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
        background-color: rgba(255, 255, 255, 0.98);
        padding: 25px;
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

    /* 5. BURBUJAS DE CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 20px 25px;
        margin-bottom: 15px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid #8FA891;
        background-color: #FDFDFD;
    }
    .stChatMessage .stAvatar {
        background-color: #8FA891 !important;
        color: white !important;
        width: 35px;
        height: 35px;
    }

    /* 6. TEXTOS */
    .stChatMessage p, .stChatMessage li {
        color: #444 !important;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 8px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stChatMessage strong {
        color: #D4AF37 !important;
        font-weight: 700;
    }
    
    /* 7. ESTILO DEL TICKET (NUEVO) */
    div[data-testid="stExpander"] {
        border: 1px solid #8FA891;
        border-radius: 10px;
        background-color: #F9FBF9;
        margin-bottom: 20px;
    }
    div[data-testid="stExpander"] summary {
        color: #556B2F !important;
        font-weight: 600;
    }

    /* 8. OCULTAR ELEMENTOS */
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

# --- CHAT (CEREBRO POLÍGLOTA UNIVERSAL) ---
system_prompt = f"""
Actúa como el asistente experto de 'Café Chic'.
MENÚ: {menu_texto}

🛑 REGLA SUPREMA DE IDIOMA:
Tu misión es derribar barreras lingüísticas.
1. DETECTA el idioma del usuario.
2. RESPONDE ESTRICTAMENTE en ese mismo idioma.
   - Si es Inglés -> Inglés 🇬🇧
   - Si es Japonés -> Japonés 🇯🇵
   - Si es Chino -> Chino 🇨🇳
   - Si es Ruso -> Ruso 🇷🇺
   - CUALQUIER OTRO -> Responde en el idioma del usuario.

GUIDELINES:
1. **TRADUCCIÓN:** Explica los ingredientes de los platos para que un extranjero entienda qué es (ej: "Tortilla" -> Spanish potato omelet).
2. **MONEDA:** Siempre en EUROS (€).
3. **VENTA:** Recomienda siempre una bebida o postre.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "¡Hola! 🌿 Bienvenido a **Café Chic**.\n\n¿Te apetece un **Brunch** completo 🥑 o prefieres ver opciones de almuerzo? ✨"}
    ]

# --- INTERFAZ PRINCIPAL ---

# 1. Títulos
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

# 2. TICKET DE COMANDA (VISIBLE EN MÓVIL Y PC) - Opción DEMO
# Inicializamos un pedido "simulado" para mostrar funcionalidad
if "pedido" not in st.session_state:
    st.session_state.pedido = [
        {"item": "🥑 Tosta Aguacate", "precio": 8.50},
        {"item": "☕ Café Latte", "precio": 2.50},
        {"item": "🍰 Tarta de Zanahoria", "precio": 4.50}
    ]

# Cálculos del ticket
total_pedido = sum(p["precio"] for p in st.session_state.pedido)
items_count = len(st.session_state.pedido)

# Renderizamos el Ticket Desplegable
with st.expander(f"🧾 TICKET ABIERTO ({items_count}) | Total: {total_pedido:.2f}€", expanded=False):
    st.markdown("### 🛒 Tu Pedido (Simulado)")
    for p in st.session_state.pedido:
        st.markdown(f"- {p['item']} ... **{p['precio']:.2f}€**")
    
    st.markdown("---")
    
    col_cocina, col_pago = st.columns(2)
    
    with col_cocina:
        # Enlace a WhatsApp para Cocina
        # NOTA: Cambia el número si quieres probarlo en tu móvil real
        texto_cocina = "👨‍🍳 *NUEVA COMANDA MESA 1*:%0A" + "%0A".join([f"- {p['item']}" for p in st.session_state.pedido])
        url_whatsapp = f"https://wa.me/34600000000?text={texto_cocina}"
        st.link_button("👨‍🍳 A Cocina", url_whatsapp, use_container_width=True)
    
    with col_pago:
        # Enlace a Stripe (Puedes poner tu enlace real de producto aquí)
        st.link_button("💳 Pagar Ahora", "https://stripe.com/es", use_container_width=True)

# 3. Renderizar Chat
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

# 4. Input usuario
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
