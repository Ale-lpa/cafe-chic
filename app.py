import streamlit as st
import json
import random
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

# --- ESTILOS CSS (DISEÑO CHIC & LIMPIO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO GENERAL */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #8FA891 25px, #8FA891 50px);
    }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.98);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    /* 2. TICKET (Cream & Gold) */
    div[data-testid="stExpander"] {
        background-color: #FFFEF0 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 12px;
        color: #333333 !important;
    }
    div[data-testid="stExpander"] > details > summary {
        background-color: #FFFEF0 !important;
        color: #556B2F !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 12px;
    }
    div[data-testid="stExpander"] p, 
    div[data-testid="stExpander"] div, 
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] li {
        color: #333333 !important;
    }

    /* 3. BOTONES */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 8px !important;
    }
    div.stButton > button:hover {
        background-color: #FDFDFD !important;
        border-color: #8FA891 !important;
        color: #556B2F !important;
    }

    /* Botón Borrar (X) */
    button[key^="btn_del_"] {
        border: none !important;
        background: transparent !important;
        color: #FF4B4B !important;
        font-weight: bold;
        font-size: 1.2rem;
    }

    /* Botón Pagar (Rojo/Salmón) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6B6B !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FF5252 !important;
    }

    /* Botón WhatsApp (Verde) */
    a[href^="https://wa.me"] button {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
    }

    /* 4. CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 18px;
    }
    .stChatMessage p {
        color: #444444 !important;
        line-height: 1.6;
    }
    
    /* 5. BARRA LATERAL */
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

    /* TÍTULOS */
    .titulo-principal {
        font-family: 'Dancing Script', cursive;
        color: #D4AF37;
        text-align: center;
        font-size: 3.5rem;
        line-height: 1;
        margin-bottom: 10px;
    }

    /* Ocultar elementos */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
MENU_DB = {
    "Tosta Aguacate": 8.50, "Huevos Benedictinos": 10.50, "Croissant Jamón": 5.50,
    "Café Latte": 2.50, "Cappuccino": 3.00, "Zumo Naranja": 3.50,
    "Mimosa": 6.00, "Tarta Zanahoria": 4.50, "Cheesecake": 5.00
}
menu_texto = ", ".join([f"{k} ({v}€)" for k,v in MENU_DB.items()])

# --- GESTIÓN DE ESTADO ---
if "pedido" not in st.session_state:
    st.session_state.pedido = []
if "pagado" not in st.session_state:
    st.session_state.pagado = False
# Generamos un ID de pedido único si no existe
if "order_id" not in st.session_state:
    st.session_state.order_id = f"CHIC-{random.randint(100, 999)}"

# --- FUNCIONES ---
def borrar_item(index):
    st.session_state.pedido.pop(index)
    st.session_state.pagado = False 

def agregar_item(nombre_plato):
    precio = MENU_DB.get(nombre_plato, 0.0)
    if precio == 0.0:
        for k, v in MENU_DB.items():
            if k.lower() in nombre_plato.lower():
                nombre_plato = k
                precio = v
                break
    st.session_state.pedido.append({"item": nombre_plato, "precio": precio})
    st.session_state.pagado = False
    return f"✅ OK: **{nombre_plato}** added/añadido."

# --- HERRAMIENTAS IA ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "agregar_al_pedido",
            "description": "Añade un plato al ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_plato": {"type": "string", "description": f"Plato exacto: {list(MENU_DB.keys())}"}
                },
                "required": ["nombre_plato"],
            },
        }
    }
]

# --- BARRA LATERAL (RECUPERADA Y CORREGIDA) ---
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
    
    st.markdown("---")
    st.markdown("### ⚙️ Demo")
    if st.button("🗑️ Reiniciar Todo"):
        st.session_state.pedido = []
        st.session_state.pagado = False
        st.session_state.order_id = f"CHIC-{random.randint(100, 999)}"
        st.session_state.messages = []
        st.rerun()

# --- CABECERA ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)

# --- TICKET DINÁMICO & LOGÍSTICA ---
total = sum(p['precio'] for p in st.session_state.pedido)
icono_ticket = "🧾" if not st.session_state.pagado else "🎟️"
# Mostramos el ID del pedido en el título
label_ticket = f"{icono_ticket} TICKET #{st.session_state.order_id} ({len(st.session_state.pedido)}) | Total: {total:.2f}€"

with st.expander(label_ticket, expanded=(len(st.session_state.pedido) > 0)):
    if not st.session_state.pedido:
        st.info("👋 El ticket está vacío. Pide algo al chat.")
    else:
        st.markdown(f"**🆔 Pedido:** `{st.session_state.order_id}`")
        
        # --- SELECTOR DE MESA O BARRA ---
        # Solo dejamos cambiarlo si no ha pagado aún
        opciones_ubicacion = ["📍 Elige tu Mesa...", "Recogida en Barra 🙋‍♂️", "Mesa 1", "Mesa 2", "Mesa 3", "Mesa 4", "Terraza 1", "Terraza 2"]
        ubicacion = st.selectbox("¿Dónde te lo servimos?", opciones_ubicacion, disabled=st.session_state.pagado, index=0)
        
        st.markdown("---")
        st.markdown("###### 🛒 Resumen:")
        for i, p in enumerate(st.session_state.pedido):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"{p['item']}")
            c2.markdown(f"**{p['precio']:.2f}€**")
            if not st.session_state.pagado:
                c3.button("❌", key=f"btn_del_{i}", on_click=borrar_item, args=(i,))
        
        st.markdown("---")
        
        if not st.session_state.pagado:
            if ubicacion == "📍 Elige tu Mesa...":
                st.warning("👇 Por favor, selecciona tu mesa o barra para pagar.")
            else:
                if st.button(f"💳 PAGAR {total:.2f}€", type="primary", use_container_width=True):
                    st.session_state.pagado = True
                    st.balloons()
                    st.rerun()
        else:
            # PANTALLA DE ÉXITO
            st.success(f"✅ ¡Pagado! Tu pedido `{st.session_state.order_id}` se está preparando.")
            
            # Preparamos el mensaje de WhatsApp con la ubicación exacta
            items_str = "%0A".join([f"▪️ {p['item']}" for p in st.session_state.pedido])
            msg_cocina = f"🔥 *NUEVO PEDIDO PAGADO* 🔥%0A🆔 *{st.session_state.order_id}*%0A📍 *UBICACIÓN:* {ubicacion}%0A------------------%0A{items_str}%0A------------------%0ATotal: {total:.2f}€"
            link_wa = f"https://wa.me/34600000000?text={msg_cocina}"
            
            st.link_button(f"👨‍🍳 ENVIAR A COCINA (WhatsApp)", link_wa, use_container_width=True)
            
            st.write("") 
            if st.button("🔄 Nuevo Pedido"):
                st.session_state.pagado = False
                st.session_state.order_id = f"CHIC-{random.randint(100, 999)}"
                st.rerun()

# --- CHATBOT ---
system_prompt = f"""
Eres 'Leo', el camarero virtual experto de 'Café Chic'. 
MENÚ Y PRECIOS: {menu_texto}

🛑 INSTRUCCIÓN DE IDIOMA CRÍTICA (POLYGLOT MODE):
1. **DETECTA EL IDIOMA DEL USUARIO.**
2. SI EL USUARIO HABLA EN INGLÉS -> **RESPONDE EN INGLÉS**.
3. SI EL USUARIO HABLA EN ESPAÑOL -> RESPONDE EN ESPAÑOL.
4. NO mezcles idiomas. Mantenlo nativo.

🌟 ESTILO:
1. Usa Emojis (🥑, 🥐, ☕).
2. Estructura con listas y pon platos/precios en **negrita**.
3. Si piden algo, usa 'agregar_al_pedido'.
"""

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for m in st.session_state.messages:
    # Corrección de lectura de objeto/dict
    if isinstance(m, dict):
        role = m["role"]
        content = m.get("content", "")
    else:
        role = m.role
        content = m.content

    if role in ["assistant", "user"] and content:
        with st.chat_message(role, avatar="🥑" if role == "assistant" else "👤"):
            st.markdown(content)

if prompt := st.chat_input("Pide aquí / Order here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages, 
        tools=tools,
        tool_choice="auto"
    )
    msg = response.choices[0].message
    msg_dict = {"role": msg.role, "content": msg.content, "tool_calls": msg.tool_calls}

    if msg.tool_calls:
        st.session_state.messages.append(msg_dict)
        for tool in msg.tool_calls:
            if tool.function.name == "agregar_al_pedido":
                args = json.loads(tool.function.arguments)
                res = agregar_item(args.get("nombre_plato"))
                st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "content": res})
        
        final_res = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": final_res.choices[0].message.content})
        st.rerun()
    else:
        st.session_state.messages.append(msg_dict)
        st.rerun()
