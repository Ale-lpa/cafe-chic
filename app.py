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

# --- ESTILOS CSS (DISEÑO CHIC & LIMPIO - ANTI DARK MODE) ---
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

    /* 2. FORZAR ESTILO DEL TICKET (Cream & Gold) */
    div[data-testid="stExpander"] {
        background-color: #FFFEF0 !important; /* Fondo Crema SIEMPRE */
        border: 1px solid #D4AF37 !important;
        border-radius: 12px;
        color: #333333 !important;
    }
    
    /* Encabezado del Ticket (Evitar que se ponga negro) */
    div[data-testid="stExpander"] > details > summary {
        background-color: #FFFEF0 !important;
        color: #556B2F !important; /* Texto Verde Oliva */
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 12px;
    }
    div[data-testid="stExpander"] > details[open] > summary {
        border-bottom: 1px solid #EAEAEA;
    }
    
    /* Contenido del Ticket */
    div[data-testid="stExpander"] p, 
    div[data-testid="stExpander"] div, 
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] li {
        color: #333333 !important; /* Texto oscuro forzado */
    }

    /* 3. BOTONES PERSONALIZADOS */
    
    /* Botones Normales (Borrar, Reiniciar) -> Blancos y Dorados */
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

    /* Botón PEQUEÑO de Borrar (X) */
    button[key^="btn_del_"] {
        border: none !important;
        background: transparent !important;
        color: #FF4B4B !important;
        font-weight: bold;
    }

    /* Botón PRIMARIO (Pagar) -> Rojo/Salmón Vibrante */
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

    /* Botón LINK (WhatsApp Cocina) -> Verde */
    a[href^="https://wa.me"] {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* 4. CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 18px;
    }
    .stChatMessage p {
        color: #444444 !important;
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

    /* OCULTAR ELEMENTOS NO DESEADOS */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DEL MENÚ ---
MENU_DB = {
    "Tosta Aguacate": 8.50,
    "Huevos Benedictinos": 10.50,
    "Croissant Jamón": 5.50,
    "Café Latte": 2.50,
    "Cappuccino": 3.00,
    "Zumo Naranja": 3.50,
    "Mimosa": 6.00,
    "Tarta Zanahoria": 4.50,
    "Cheesecake": 5.00
}
menu_texto = ", ".join([f"{k} ({v}€)" for k,v in MENU_DB.items()])

# --- GESTIÓN DE ESTADO ---
if "pedido" not in st.session_state:
    st.session_state.pedido = []
if "pagado" not in st.session_state:
    st.session_state.pagado = False

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
    return f"Añadido {nombre_plato}."

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
                    "nombre_plato": {"type": "string", "description": f"Plato exacto del menú: {list(MENU_DB.keys())}"}
                },
                "required": ["nombre_plato"],
            },
        }
    }
]

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ Demo")
    if st.button("🗑️ Reiniciar Todo"):
        st.session_state.pedido = []
        st.session_state.pagado = False
        st.session_state.messages = []
        st.rerun()

# --- CABECERA ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)

# --- TICKET DINÁMICO ---
total = sum(p['precio'] for p in st.session_state.pedido)
icono_ticket = "🧾" if not st.session_state.pagado else "🎟️"
label_ticket = f"{icono_ticket} TICKET MESA 5 ({len(st.session_state.pedido)}) | Total: {total:.2f}€"

# Renderizado del Ticket
with st.expander(label_ticket, expanded=(len(st.session_state.pedido) > 0)):
    if not st.session_state.pedido:
        st.info("👋 El ticket está vacío. Pide algo al chat.")
    else:
        st.markdown("###### 🛒 Tu Pedido:")
        for i, p in enumerate(st.session_state.pedido):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"{p['item']}")
            c2.markdown(f"**{p['precio']:.2f}€**")
            
            if not st.session_state.pagado:
                c3.button("❌", key=f"btn_del_{i}", on_click=borrar_item, args=(i,))
        
        st.markdown("---")
        
        if not st.session_state.pagado:
            st.caption("🔒 *Paga para enviar a cocina.*")
            if st.button(f"💳 PAGAR {total:.2f}€", type="primary", use_container_width=True):
                st.session_state.pagado = True
                st.balloons()
                st.rerun()
        else:
            st.success("✅ ¡Pago Confirmado!")
            
            items_str = "%0A".join([f"▪️ {p['item']}" for p in st.session_state.pedido])
            msg_cocina = f"🔥 *COMANDA PAGADA* 🔥%0A------------------%0A{items_str}%0A------------------%0AMesa: 5%0ATotal: {total:.2f}€"
            link_wa = f"https://wa.me/34600000000?text={msg_cocina}"
            
            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:10px; width:100%; border-radius:8px; font-weight:bold; font-size:16px;">👨‍🍳 ENVIAR A COCINA (WhatsApp)</button></a>', unsafe_allow_html=True)
            
            st.write("") # Espacio
            if st.button("🔄 Pedir más"):
                st.session_state.pagado = False
                st.rerun()

# --- CHATBOT ---
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": f"Eres un camarero. Menú: {menu_texto}. Si piden, usa 'agregar_al_pedido'. Idioma: Detecta y responde igual."}
    ]

for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"]:
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

if prompt := st.chat_input("Pide aquí..."):
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

    if msg.tool_calls:
        st.session_state.messages.append(msg)
        for tool in msg.tool_calls:
            if tool.function.name == "agregar_al_pedido":
                args = json.loads(tool.function.arguments)
                res = agregar_item(args.get("nombre_plato"))
                st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "content": res})
        
        final_res = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": final_res.choices[0].message.content})
        st.rerun()
    else:
        st.session_state.messages.append({"role": "assistant", "content": msg.content})
        st.rerun()
