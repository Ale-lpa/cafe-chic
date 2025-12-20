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

# --- ESTILOS CSS (DISEÑO PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Helvetica+Neue:wght@300;400;600&display=swap');

    /* 1. FONDO GENERAL */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
        background-image: repeating-linear-gradient(90deg, #FFFFFF, #FFFFFF 25px, #8FA891 25px, #8FA891 50px);
    }
    
    /* 2. CONTENEDOR PRINCIPAL (TARJETA) */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.98);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-width: 700px;
    }

    /* 3. TÍTULOS (LO QUE FALTABA) */
    .titulo-principal {
        font-family: 'Dancing Script', cursive;
        color: #D4AF37; /* Dorado */
        text-align: center;
        font-size: 3.8rem; /* Bien grande */
        line-height: 1.1;
        margin-top: 0px;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.05);
    }
    .subtitulo {
        text-align: center;
        color: #8FA891; /* Verde Chic */
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 4px;
        font-size: 0.9rem;
        margin-bottom: 25px;
    }

    /* 4. TICKET (Color Crema y Texto Oscuro) */
    div[data-testid="stExpander"] {
        background-color: #FFFEF0 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    div[data-testid="stExpander"] summary {
        color: #556B2F !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stExpander"] p, span, div, li {
        color: #333333 !important;
    }

    /* 5. BOTONES */
    div.stButton > button {
        background-color: white;
        border: 1px solid #D4AF37;
        color: #333;
        border-radius: 8px;
    }
    div.stButton > button[kind="primary"] { /* Botón Pagar */
        background-color: #FF6B6B !important;
        color: white !important;
        border: none !important;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);
    }

    /* Botón WhatsApp */
    a[href^="https://wa.me"] button {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        font-weight: bold;
    }
    
    /* 6. CHAT */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #F0F0F0;
        border-radius: 15px;
    }

    /* OCULTAR COSAS */
    [data-testid="stHeader"], footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DEL MENÚ ---
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

# --- ESTADO ---
if "pedido" not in st.session_state: st.session_state.pedido = []
if "pagado" not in st.session_state: st.session_state.pagado = False

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
    return f"✅ Anotado: **{nombre_plato}**"

# --- TOOLS ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Demo")
    if st.button("🗑️ Reiniciar Demo"):
        st.session_state.pedido = []
        st.session_state.pagado = False
        st.session_state.messages = []
        st.rerun()

# --- HEADER (TÍTULO RECUPERADO) ---
st.markdown('<div class="titulo-principal">Café Chic</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Asistente Virtual</div>', unsafe_allow_html=True)

# --- TICKET ---
total = sum(p['precio'] for p in st.session_state.pedido)
label_ticket = f"🧾 TICKET MESA 5 ({len(st.session_state.pedido)}) | Total: {total:.2f}€"
if st.session_state.pagado: label_ticket = f"🎟️ TICKET PAGADO | Total: {total:.2f}€"

with st.expander(label_ticket, expanded=(len(st.session_state.pedido) > 0)):
    if not st.session_state.pedido:
        st.info("Tu cuenta está vacía. Pide algo al camarero. 🥑")
    else:
        st.markdown("###### 🛒 Tu Pedido:")
        for i, p in enumerate(st.session_state.pedido):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"{p['item']}")
            c2.markdown(f"**{p['precio']:.2f}€**")
            if not st.session_state.pagado:
                c3.button("❌", key=f"del_{i}", on_click=borrar_item, args=(i,))
        
        st.markdown("---")
        
        if not st.session_state.pagado:
            if st.button(f"💳 PAGAR {total:.2f}€", type="primary", use_container_width=True):
                st.session_state.pagado = True
                st.balloons()
                st.rerun()
        else:
            st.success("✅ ¡Pago Confirmado! Pedido enviado a cocina.")
            items_str = "%0A".join([f"▪️ {p['item']}" for p in st.session_state.pedido])
            msg = f"🔥 *NUEVA COMANDA* 🔥%0A------------------%0A{items_str}%0A------------------%0AMesa: 5%0APAGADO: {total:.2f}€"
            link = f"https://wa.me/34600000000?text={msg}"
            st.link_button("👨‍🍳 ENVIAR A COCINA (WhatsApp)", link, use_container_width=True)
            if st.button("🔄 Pedir más"):
                st.session_state.pagado = False
                st.rerun()

# --- CHATBOT ---
system_prompt = f"""
Eres 'Leo', el camarero virtual de 'Café Chic'. 
MENÚ: {menu_texto}

REGLA DE ORO (IDIOMA):
1. Detecta el idioma del usuario (Inglés, Chino, Ruso, etc).
2. Responde SIEMPRE en ese mismo idioma.

ESTILO:
- Usa emojis (🥑, ☕, ✨).
- Sé breve y usa listas.
- Nombres de platos en **negrita**.
- Si piden comida, usa la función 'agregar_al_pedido'.
"""

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for m in st.session_state.messages:
    if m["role"] in ["assistant", "user"] and m.get("content"):
        with st.chat_message(m["role"], avatar="🥑" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])

if prompt := st.chat_input("Pide aquí... (Ej: Café y Tosta)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Guardar mensaje limpio
        msg_dict = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = [{"id": t.id, "type": t.type, "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in msg.tool_calls]
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

    except Exception as e:
        st.error(f"Error: {e}")
