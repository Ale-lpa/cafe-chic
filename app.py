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

# --- ESTILOS CSS (DISEÑO CHIC & LIMPIO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO */
    [data-testid="stAppViewContainer"] {
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #8FA891 25px, #8FA891 50px);
    }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.98);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    /* 2. TICKET ELEGANTE */
    div[data-testid="stExpander"] {
        border: 1px solid #D4AF37;
        background-color: #FFFEF0; /* Fondo crema suave */
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] summary {
        color: #556B2F !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stExpander"] p, span, div {
        color: #333333 !important; /* Texto oscuro para lectura fácil */
    }

    /* 3. BOTONES PERSONALIZADOS */
    /* Botón Borrar (Pequeño y sutil) */
    button[key^="btn_del_"] {
        border: none;
        background: transparent;
        color: #FF4B4B;
        font-size: 1.2rem;
        padding: 0;
    }
    button[key^="btn_del_"]:hover {
        color: #ff0000;
        background: transparent;
    }

    /* 4. CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 18px;
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid #8FA891;
        background-color: #FDFDFD;
    }

    /* OCULTAR ELEMENTOS SOBRANTES */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {visibility: hidden;}
    
    /* TÍTULOS */
    .titulo-principal {
        font-family: 'Dancing Script', cursive;
        color: #D4AF37;
        text-align: center;
        font-size: 3.5rem;
        line-height: 1;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DEL MENÚ (Precios Reales) ---
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
    # Si borras algo, asumimos que cambia el pedido y hay que pagar de nuevo si ya estaba pagado
    st.session_state.pagado = False 

def agregar_item(nombre_plato):
    precio = MENU_DB.get(nombre_plato, 0.0)
    # Búsqueda aproximada si no es exacto
    if precio == 0.0:
        for k, v in MENU_DB.items():
            if k.lower() in nombre_plato.lower():
                nombre_plato = k
                precio = v
                break
    
    st.session_state.pedido.append({"item": nombre_plato, "precio": precio})
    st.session_state.pagado = False # Al añadir algo nuevo, el estado vuelve a "No Pagado"
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

# --- INTERFAZ BARRA LATERAL (DEBUG) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    if st.button("🗑️ Reiniciar Demo"):
        st.session_state.pedido = []
        st.session_state.pagado = False
        st.session_state.messages = []
        st.rerun()

# --- CABECERA ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)

# --- TICKET DINÁMICO (LA JOYA DE LA CORONA) ---
total = sum(p['precio'] for p in st.session_state.pedido)
estado_pago = "✅ PAGADO" if st.session_state.pagado else "⏳ PENDIENTE"
icono_ticket = "🧾" if not st.session_state.pagado else "🎟️"

label_ticket = f"{icono_ticket} TICKET MESA 5 ({len(st.session_state.pedido)}) | Total: {total:.2f}€"

with st.expander(label_ticket, expanded=(len(st.session_state.pedido) > 0)):
    if not st.session_state.pedido:
        st.info("👋 El ticket está vacío. Pide algo al chat (ej: 'Quiero un café').")
    else:
        # 1. LISTADO DE PRODUCTOS
        st.markdown("###### 🛒 Resumen del pedido:")
        for i, p in enumerate(st.session_state.pedido):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"{p['item']}")
            c2.markdown(f"**{p['precio']:.2f}€**")
            
            # Botón Borrar (Solo si no está pagado, para evitar líos)
            if not st.session_state.pagado:
                c3.button("❌", key=f"btn_del_{i}", on_click=borrar_item, args=(i,))
        
        st.markdown("---")
        
        # 2. ZONA DE ACCIÓN (PAGO -> COCINA)
        col_accion = st.container()
        
        if not st.session_state.pagado:
            # FASE 1: PAGAR
            st.caption("🔒 *La comanda se enviará a cocina automáticamente tras el pago.*")
            if st.button(f"💳 PAGAR {total:.2f}€ AHORA", type="primary", use_container_width=True):
                st.session_state.pagado = True
                st.balloons() # ¡FIESTA!
                st.rerun()
        else:
            # FASE 2: ENVIAR A COCINA (WhatsApp)
            st.success("✅ ¡Pago Confirmado! El pedido está listo para marchar.")
            
            items_str = "%0A".join([f"▪️ {p['item']}" for p in st.session_state.pedido])
            msg_cocina = f"🔥 *NUEVA COMANDA PAGADA* 🔥%0A------------------%0A{items_str}%0A------------------%0AMesa: 5%0ATotal: {total:.2f}€"
            link_wa = f"https://wa.me/34600000000?text={msg_cocina}"
            
            st.link_button("👨‍🍳 ENVIAR A COCINA (WhatsApp)", link_wa, use_container_width=True)
            
            if st.button("🔄 Nuevo Pedido / Añadir más"):
                st.session_state.pagado = False
                st.rerun()

# --- CHATBOT ---
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": f"Eres un camarero experto. Menú: {menu_texto}. Si piden algo, usa 'agregar_al_pedido'. Idioma: Detecta y responde igual."}
    ]

# Renderizar chat
for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"]:
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

# Input
if prompt := st.chat_input("Pide aquí (ej: Un café y una tarta)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Llamada a GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto"
    )
    msg = response.choices[0].message

    # ¿Usó herramienta?
    if msg.tool_calls:
        st.session_state.messages.append(msg)
        for tool in msg.tool_calls:
            if tool.function.name == "agregar_al_pedido":
                args = json.loads(tool.function.arguments)
                res = agregar_item(args.get("nombre_plato"))
                st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "content": res})
        
        # Respuesta final tras añadir
        final_res = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": final_res.choices[0].message.content})
        st.rerun()
    else:
        st.session_state.messages.append({"role": "assistant", "content": msg.content})
        st.rerun()
