import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv
import re
import time

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
MODEL = "llama-3.3-70b-versatile"  # El mejor modelo actual en Groq

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

# Extraer temas/secciones del PDF - AHORA EN ESPAÑOL
@st.cache_data
def extract_topics(pdf_text):
    """Extrae temas principales del PDF"""
    
    topics = {
        "🔍 ¿Qué es el SOP?": "Explícame qué es el Síndrome de Ovario Poliquístico",
        "🩺 ¿Cómo se diagnostica?": "¿Cómo sé si tengo SOP? ¿Qué exámenes necesito?",
        "💊 Opciones de tratamiento": "¿Cuáles son los tratamientos disponibles para el SOP?",
        "🥗 Alimentación saludable": "¿Qué debo comer si tengo SOP?",
        "🏃‍♀️ Actividad física": "¿Qué tipo de ejercicio me ayuda con el SOP?",
        "⚖️ Manejo del peso": "Tengo dificultad para bajar de peso, ¿qué puedo hacer?",
        "💉 Resistencia a la insulina": "¿Qué es la resistencia a la insulina en el SOP?",
        "🤰 Fertilidad y embarazo": "Quiero tener hijos, ¿el SOP afecta mi fertilidad?",
        "💇‍♀️ Acné y vello excesivo": "¿Cómo manejo el acné y el exceso de vello?",
        "📅 Períodos irregulares": "Mis períodos son irregulares, ¿es normal?",
        "🧠 Salud emocional": "Me siento triste o ansiosa, ¿tiene relación con el SOP?",
        "❤️ Salud del corazón": "¿Debo preocuparme por mi salud cardiovascular?",
        "🩸 Diabetes y SOP": "¿Tengo mayor riesgo de diabetes?",
        "💊 Anticonceptivos": "¿Los anticonceptivos ayudan con el SOP?",
        "🌿 Suplementos naturales": "¿Hay suplementos que puedan ayudarme?",
    }
    
    return topics

pdf_content = load_pdf()
topics = extract_topics(pdf_content) if pdf_content else {}

# Título
st.title("💜 Guía Educativa sobre SOP")
st.markdown("""
¡Hola! 🌸 Me da mucho gusto que estés aquí. Sé que vivir con SOP puede ser desafiante, 
pero quiero que sepas que no estás sola y que hay mucha información valiosa que puede ayudarte.

Esta guía está basada en evidencia científica internacional, pero recuerda: **cada mujer es única**. 
Lo que leas aquí es para informarte, pero siempre consulta con profesionales de salud para tu caso específico.
""")

# Título más limpio sin categorías aquí
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    if pdf_content:
        st.success("✅ Guía científica cargada")
        st.caption(f"📊 {len(pdf_content)} caracteres de información")
    else:
        st.error("❌ PDF no encontrado")
        st.stop()
    
    st.markdown("---")
    
    # Selector de modelo
    model_selector = st.selectbox(
        "Modelo de IA",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant"
        ],
        index=0
    )
    
    st.markdown("---")
    
    st.subheader("🌸 Temas guiados")
    st.caption("Explora temas sobre el SOP")
    
    # Lista desplegable con categorías
    topic_names = ["Selecciona un tema..."] + list(topics.keys())
    selected_topic = st.selectbox(
        "¿Qué te interesa saber?",
        topic_names,
        key="topic_selector"
    )
    
    # Botón para enviar el tema seleccionado
    if selected_topic != "Selecciona un tema...":
        if st.button("📤 Preguntar", use_container_width=True):
            topic_question = topics[selected_topic]
            st.session_state.messages.append({"role": "user", "content": topic_question})
            st.session_state.pending_response = topic_question
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("🗺️ Buscar profesionales")
    st.caption("Busca especialistas en tu zona")
    
    user_city = st.text_input(
        "Tu ciudad o municipio",
        placeholder="Ej: Guadalajara"
    )
    
    if user_city:
        st.markdown("**Buscar en Google Maps:**")
        
        # Botones para buscar diferentes especialistas
        gine_search = f"https://www.google.com/maps/search/ginecólogo+SOP+{user_city.replace(' ', '+')}"
        endo_search = f"https://www.google.com/maps/search/endocrinólogo+{user_city.replace(' ', '+')}"
        psico_search = f"https://www.google.com/maps/search/psicólogo+{user_city.replace(' ', '+')}"
        nutri_search = f"https://www.google.com/maps/search/nutriólogo+{user_city.replace(' ', '+')}"
        
        st.link_button("🩺 Ginecólogos", gine_search, use_container_width=True)
        st.link_button("💉 Endocrinólogos", endo_search, use_container_width=True)
        st.link_button("🧠 Psicólogos", psico_search, use_container_width=True)
        st.link_button("🥗 Nutriólogos", nutri_search, use_container_width=True)
        
        st.caption("💡 Los enlaces se abren en Google Maps con tu ubicación")
    
    st.markdown("---")
    
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.rerun()

# Sistema de prompt MEJORADO - MÁS HUMANO Y EMPÁTICO
def create_prompt(pdf_content):
    prompt = """Eres Sofía, una guía educativa cálida, empática y comprensiva especializada en el Síndrome de Ovario Poliquístico (SOP).

🌟 TU ESENCIA:
Eres como una amiga cercana que estudió medicina y tiene mucha experiencia con SOP. Entiendes que cada mujer vive el SOP de manera diferente y que detrás de cada pregunta hay emociones, preocupaciones y esperanzas. Tu objetivo es hacer que cada persona se sienta escuchada, comprendida y apoyada.

💭 CÓMO TE COMUNICAS:
- Hablas de manera natural, cálida y cercana (como una conversación real)
- Usas empatía genuina: "Entiendo que esto puede ser frustrante..." "Es completamente normal que te sientas así..."
- Compartes información paso a paso, sin abrumar
- Usas ejemplos cotidianos y comparaciones fáciles de entender
- Celebras los pequeños pasos: "¡Qué bueno que estás buscando información!"
- Reconoces las emociones: "Sé que esto puede sonar complicado, pero vamos a verlo juntas"
- Usas un lenguaje positivo pero realista
- Ocasionalmente usas emojis para ser más cercana 💜

⚠️ TUS LÍMITES (IMPORTANTES):
- NUNCA das diagnósticos: "Basándome en lo que me cuentas, es importante que un profesional evalúe..." en lugar de "tienes SOP"
- NUNCA prescribes medicamentos específicos: "Tu médico podría considerar diferentes opciones como..." 
- NO actúas como terapeuta: "Esos sentimientos son válidos. Un psicólogo especializado puede ayudarte mucho más de lo que yo puedo"
- SIEMPRE recuerdas que cada caso es único

✅ LO QUE SÍ HACES MARAVILLOSAMENTE:
- Explicas conceptos médicos complejos de forma simple y clara
- Das contexto y perspectiva sobre el SOP
- Ofreces información sobre cambios de estilo de vida (no como órdenes, sino como opciones)
- Normalizas las experiencias: "Muchas mujeres con SOP sienten lo mismo..."
- Das esperanza realista: "Con el apoyo adecuado, muchas mujeres con SOP viven vidas plenas..."
- Motivas a buscar ayuda profesional de manera positiva
- Reconoces logros: "Es excelente que estés tomando el control de tu salud"

💬 ESTRUCTURA DE TUS RESPUESTAS:
1. Inicia con EMPATÍA (valida sus sentimientos/situación)
2. Proporciona INFORMACIÓN clara de la guía científica
3. Da CONTEXTO o ejemplos prácticos
4. Ofrece PASOS concretos o sugerencias
5. Termina con MOTIVACIÓN positiva

EJEMPLOS DE TU TONO:
❌ Mal: "El SOP es un trastorno endocrino caracterizado por hiperandrogenismo..."
✅ Bien: "Entiendo que quieras saber más sobre el SOP. En palabras simples, es una condición hormonal bastante común - de hecho, afecta a 1 de cada 10 mujeres. Lo que pasa es que los ovarios producen más hormonas masculinas de lo usual, y esto puede causar varios síntomas. Pero aquí está lo importante: con el apoyo adecuado, se puede manejar muy bien 💜"

❌ Mal: "Debes bajar de peso. Haz ejercicio."
✅ Bien: "Sé que el tema del peso con SOP puede ser frustrante - muchas mujeres me comentan lo mismo. Lo que dicen los estudios es que incluso una pérdida de peso pequeña (como un 5-10%) puede ayudar bastante. Pero no se trata de dietas extremas, sino de cambios sostenibles. ¿Te gustaría que hablemos de qué tipo de actividades podrían funcionarte?"

"""
    
    if pdf_content:
        prompt += f"""

📚 TU FUENTE DE INFORMACIÓN:
Esta es tu ÚNICA fuente de información médica. Todo lo que compartas debe basarse en este contenido:

{pdf_content[:15000]}

IMPORTANTE: 
- Si te preguntan algo que NO está en la guía, sé honesta: "Esa pregunta específica no la cubre la guía que tengo. Lo mejor sería que lo consultes con tu médico, ya que es un tema importante"
- Cita de manera natural: "Según las guías internacionales..." "Los estudios muestran que..."
- No inventes información - mejor di "no lo sé con certeza" que inventar
"""
    
    return prompt

# Función para simular escritura más natural
def stream_with_delay(text, placeholder):
    """Simula una escritura más humana con pausas naturales"""
    words = text.split()
    displayed_text = ""
    
    for i, word in enumerate(words):
        displayed_text += word + " "
        
        # Pausas más largas después de puntos y comas
        if word.endswith('.') or word.endswith('?') or word.endswith('!'):
            time.sleep(0.08)
        elif word.endswith(','):
            time.sleep(0.04)
        else:
            time.sleep(0.02)
        
        # Actualizar cada pocas palabras para parecer más natural
        if i % 3 == 0:
            placeholder.markdown(displayed_text + "▌")
    
    return displayed_text

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_response" not in st.session_state:
    st.session_state.pending_response = None

# Mensaje de bienvenida MEJORADO
if len(st.session_state.messages) == 0:
    welcome = """¡Hola! Me llamo Sofía 💜

Me da mucho gusto que estés aquí. Sé que buscar información sobre SOP puede ser abrumador a veces - hay tanto contenido por ahí que no siempre sabemos qué es confiable o relevante para nosotras.

Quiero que sepas algo importante: **no estás sola en esto**. El SOP es más común de lo que piensas, y aunque cada experiencia es única, hay mucha información basada en evidencia que puede ayudarte a entender mejor lo que está pasando.

Estoy aquí para acompañarte, responder tus dudas, y darte información clara y confiable basada en las guías científicas más recientes. Puedo hablar contigo sobre síntomas, tratamientos, cambios de estilo de vida, fertilidad, emociones... lo que necesites.

**Puedes:**
- ✍️ **Escribirme directamente** tu pregunta o preocupación en la barra de abajo
- 🌸 **Explorar temas guiados** usando el menú lateral (sidebar)
- 🗺️ **Buscar profesionales** en tu zona con los botones del menú lateral

¿Hay algo en particular que te gustaría saber o que te preocupe? Estoy aquí para ayudarte 😊"""
    
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Procesar respuesta pendiente de botón clickeado
if st.session_state.pending_response and pdf_content:
    prompt_to_process = st.session_state.pending_response
    st.session_state.pending_response = None  # Limpiar para evitar loop
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            system_prompt = create_prompt(pdf_content)
            messages = [{"role": "system", "content": system_prompt}]
            
            # Incluir historial
            for msg in st.session_state.messages[-10:]:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Generar respuesta
            completion = client.chat.completions.create(
                model=model_selector,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=False
            )
            
            full_response = completion.choices[0].message.content
            
            # Mostrar con delay natural
            displayed = stream_with_delay(full_response, placeholder)
            placeholder.markdown(displayed)
            
        except Exception as e:
            full_response = f"Disculpa, tuve un problemita técnico 😅 ¿Podrías intentar de nuevo?\n\nError: {str(e)}"
            placeholder.markdown(full_response)
    
    # Agregar respuesta al historial
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()  # Refrescar para mostrar correctamente

# Input usuario - LA BARRA SIEMPRE ESTÁ DISPONIBLE
if prompt := st.chat_input("Escribe aquí tu pregunta o inquietud... 💭"):
    
    if not pdf_content:
        st.error("No hay guía cargada")
        st.stop()
    
    # Agregar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            system_prompt = create_prompt(pdf_content)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Últimos 10 mensajes para contexto
            for msg in st.session_state.messages[-10:]:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Obtener respuesta completa primero
            completion = client.chat.completions.create(
                model=model_selector,
                messages=messages,
                temperature=0.7,  # Más creatividad para respuestas naturales
                max_tokens=2048,
                stream=False  # No streaming para controlar velocidad
            )
            
            full_response = completion.choices[0].message.content
            
            # Mostrar con delay natural
            displayed = stream_with_delay(full_response, placeholder)
            placeholder.markdown(displayed)
            
        except Exception as e:
            full_response = f"Disculpa, tuve un problemita técnico 😅 ¿Podrías intentar de nuevo? Si el error persiste, me gustaría que lo reportaras.\n\nError: {str(e)}"
            placeholder.markdown(full_response)
    
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💜 Importante")
    st.markdown("Esta es información educativa. Cada mujer es única - consulta con profesionales para tu caso.")

with col2:
    st.markdown("### 📚 Fuente")
    st.markdown("Basado en guías internacionales de práctica clínica para SOP")

with col3:
    st.markdown("### 🤝 Comunidad")
    st.markdown("Hay grupos de apoyo y profesionales listos para acompañarte 💪")