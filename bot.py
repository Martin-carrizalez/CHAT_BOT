import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Guía Educativa SOP",
    page_icon="💜",
    layout="wide"
)

# CONFIGURACIÓN - EDITA AQUÍ
GROQ_API_KEY = "gsk_tu_api_key_aqui"  # Reemplaza con tu API key
PDF_PATH = "guia_sop.pdf"  # Nombre de tu PDF
MODEL = "llama-3.3-70b-versatile"

# Intentar obtener la API key de variables de entorno primero
if os.getenv("GROQ_API_KEY"):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inicializar cliente de Groq
@st.cache_resource
def init_client():
    return Groq(api_key=GROQ_API_KEY)

client = init_client()

# Cargar el PDF
@st.cache_data
def load_pdf():
    if not os.path.exists(PDF_PATH):
        st.error(f"❌ No se encuentra el archivo: {PDF_PATH}")
        st.info("Asegúrate de que el PDF esté en la misma carpeta que este script")
        return None
    
    try:
        with open(PDF_PATH, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        st.error(f"Error al leer el PDF: {str(e)}")
        return None

pdf_content = load_pdf()

# Título
st.title("💜 Guía Educativa sobre SOP")
st.markdown("""
¡Bienvenida! 🌸 Estoy aquí para ayudarte a entender mejor el Síndrome de Ovario Poliquístico 
basándome en información científica y confiable.

**Recuerda:** Esta es una herramienta educativa. Para diagnósticos y tratamientos, 
siempre consulta con profesionales de la salud.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    if pdf_content:
        st.success("✅ Guía cargada correctamente")
        st.caption(f"📊 {len(pdf_content)} caracteres")
    else:
        st.error("❌ PDF no encontrado")
        st.stop()
    
    st.markdown("---")
    
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.4, 0.1)
    max_tokens = st.slider("Máx tokens", 512, 4096, 2048, 128)
    
    st.markdown("---")
    
    st.subheader("📍 Tu ubicación")
    user_location = st.text_input(
        "Ciudad",
        placeholder="ej: Guadalajara, Jalisco"
    )
    
    st.markdown("---")
    
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.rerun()

# Sistema de prompt
def create_prompt(pdf_content, location):
    prompt = """Eres una guía educativa cálida y amigable sobre el Síndrome de Ovario Poliquístico (SOP).

🌟 PERSONALIDAD:
- Cálida, comprensiva y cercana
- Positiva y motivadora
- Educativa sin ser intimidante
- Empática

⚠️ NUNCA HAGAS:
- Diagnósticos
- Prescribir tratamientos o medicamentos
- Actuar como psicóloga
- Reemplazar consulta médica

✅ SÍ HACES:
- Explicar el SOP claramente
- Compartir info de la guía científica
- Orientar sobre estilo de vida
- Motivar a buscar ayuda profesional
- Normalizar experiencias
- Dar esperanza

"""
    
    if pdf_content:
        prompt += f"""
📚 GUÍA CIENTÍFICA (usa SOLO esta información):

{pdf_content[:10000]}

Basa TODAS tus respuestas en esta guía.
"""
    
    if location:
        prompt += f"""
📍 Usuario en: {location}
Si busca profesionales, sugiere búsquedas locales en Google, directorios médicos, etc.
"""
    
    return prompt

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mensaje de bienvenida
if len(st.session_state.messages) == 0:
    welcome = """¡Hola! 👋 Me da mucho gusto que estés aquí.

Puedes preguntarme sobre:
🌸 **Qué es el SOP** - Síntomas, causas, diagnóstico
🥗 **Estilo de vida** - Alimentación, ejercicio
💜 **Apoyo emocional** - Cómo sobrellevar el SOP
👩‍⚕️ **Profesionales** - Dónde encontrar especialistas

¿En qué puedo ayudarte hoy? 😊"""
    
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input usuario
if prompt := st.chat_input("Escribe tu pregunta... 💭"):
    
    if not pdf_content:
        st.error("No hay guía cargada")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            system_prompt = create_prompt(pdf_content, user_location)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in st.session_state.messages[-10:]:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Error: {str(e)}"
            placeholder.markdown(full_response)
    
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💜 Recuerda")
    st.markdown("Esta es una herramienta educativa. Consulta con profesionales.")

with col2:
    st.markdown("### 📚 Recursos")
    st.markdown("- [PCOS Awareness](https://www.pcosaa.org/)\n- [OMS](https://www.who.int/)")

with col3:
    st.markdown("### 🤝 Apoyo")
    st.markdown("No estás sola. Hay profesionales listos para apoyarte.")