import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv
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
MODEL = "llama-3.3-70b-versatile"

# Intentar obtener la API key de variables de entorno primero
if os.getenv("GROQ_API_KEY"):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inicializar cliente de Groq
@st.cache_resource
def init_client():
    return Groq(api_key=GROQ_API_KEY)

client = init_client()

# Cargar el PDF y dividir en chunks
@st.cache_data
def load_and_chunk_pdf():
    if not os.path.exists(PDF_PATH):
        st.error(f"❌ No se encuentra el archivo: {PDF_PATH}")
        return None, []
    
    try:
        with open(PDF_PATH, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Dividir en chunks de ~2000 caracteres
        chunk_size = 2000
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return text, chunks
    except Exception as e:
        st.error(f"Error al leer el PDF: {str(e)}")
        return None, []

# Buscar chunks relevantes basado en la pregunta
def find_relevant_chunks(query, chunks, client, top_k=3):
    """Busca los chunks más relevantes para la pregunta usando embeddings simulados"""
    if not chunks:
        return []
    
    # Si la pregunta tiene keywords específicos, buscar por keyword
    query_lower = query.lower()
    keywords = {
        'diagnóstico': ['diagnóstico', 'criterios', 'rotterdam', 'examen'],
        'tratamiento': ['tratamiento', 'medicamento', 'terapia'],
        'dieta': ['dieta', 'alimentación', 'comida', 'nutrición'],
        'ejercicio': ['ejercicio', 'actividad física', 'deporte'],
        'peso': ['peso', 'obesidad', 'adelgazar'],
        'fertilidad': ['fertilidad', 'embarazo', 'bebé', 'concepción'],
        'síntomas': ['síntomas', 'signos', 'manifestaciones'],
        'insulina': ['insulina', 'glucosa', 'diabetes'],
        'mental': ['depresión', 'ansiedad', 'emocional', 'psicológico'],
        'anticonceptivos': ['anticonceptivos', 'píldora', 'hormonal']
    }
    
    # Encontrar categoría relevante
    relevant_keywords = []
    for category, words in keywords.items():
        if any(word in query_lower for word in words):
            relevant_keywords.extend(words)
    
    # Buscar chunks que contengan keywords relevantes
    scored_chunks = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for keyword in relevant_keywords if keyword in chunk_lower)
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # Ordenar por relevancia
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    
    # Retornar top_k chunks más relevantes
    return [chunk for score, chunk in scored_chunks[:top_k]]

pdf_content, pdf_chunks = load_and_chunk_pdf()

# Temas predefinidos
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

# Título
st.markdown('<h1 style="color: #9b59b6; margin-bottom: 5px;">💜 Guía Educativa sobre SOP</h1>', unsafe_allow_html=True)
st.markdown("""
¡Hola! 🌸 Soy Sofía, tu guía educativa sobre el Síndrome de Ovario Poliquístico.

Me baso exclusivamente en la **Guía Internacional de Práctica Clínica para el SOP** (Monash 2023) 
para darte información confiable y basada en evidencia científica.

**Importante:** Solo puedo ayudarte con temas relacionados al SOP. Para otras consultas médicas 
o temas fuera del SOP, por favor consulta con un profesional de salud.
""")

st.markdown("---")

# Sidebar
with st.sidebar:
    with st.sidebar:
        st.image("logo.png", width=250)
        st.markdown("---")
        st.header("⚙️ Configuración")
    
    
    if pdf_content:
        st.success("✅ Guía científica cargada")
        st.caption(f"📊 {len(pdf_content)} caracteres")
        st.caption(f"📑 {len(pdf_chunks)} secciones")
    else:
        st.error("❌ PDF no encontrado")
        st.stop()
    
    st.markdown("---")
    
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
    
    topic_names = ["Selecciona un tema..."] + list(topics.keys())
    selected_topic = st.selectbox(
        "¿Qué te interesa saber?",
        topic_names,
        key="topic_selector"
    )
    
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
        
        gine_search = f"https://www.google.com/maps/search/ginecólogo+SOP+{user_city.replace(' ', '+')}"
        endo_search = f"https://www.google.com/maps/search/endocrinólogo+{user_city.replace(' ', '+')}"
        psico_search = f"https://www.google.com/maps/search/psicólogo+{user_city.replace(' ', '+')}"
        nutri_search = f"https://www.google.com/maps/search/nutriólogo+{user_city.replace(' ', '+')}"
        
        st.link_button("🩺 Ginecólogos", gine_search, use_container_width=True)
        st.link_button("💉 Endocrinólogos", endo_search, use_container_width=True)
        st.link_button("🧠 Psicólogos", psico_search, use_container_width=True)
        st.link_button("🥗 Nutriólogos", nutri_search, use_container_width=True)
        
        st.caption("💡 Los enlaces se abren en Google Maps")
    
    st.markdown("---")
    
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.session_state.pending_response = None
        st.rerun()

# Prompt mejorado con restricciones ESTRICTAS
def create_prompt(relevant_context):
    prompt = f"""Eres Sofía, una guía educativa especializada EXCLUSIVAMENTE en el Síndrome de Ovario Poliquístico (SOP).

🚨 RESTRICCIONES ABSOLUTAS:

1. **SOLO hablas de SOP**: Si te preguntan sobre CUALQUIER otro tema (física, otros problemas de salud, hombres, etc.), debes responder:
   "Lo siento, solo puedo ayudarte con información sobre el Síndrome de Ovario Poliquístico (SOP) en mujeres. Para otras consultas médicas o temas, te recomiendo consultar con un profesional de salud apropiado. ¿Tienes alguna pregunta sobre el SOP? 😊"

2. **SOP es EXCLUSIVO de mujeres**: Si un hombre pregunta si tiene SOP, responde amablemente que el SOP es una condición que SOLO afecta a mujeres y que debe consultar con su médico para sus síntomas específicos.

3. **SOLO usas la información del contexto proporcionado**: NO inventes, NO uses conocimiento general. Si la información NO está en el contexto, di: "Esa información específica no está en la guía que tengo disponible. Te recomiendo consultar con tu ginecólogo o endocrinólogo para esa pregunta específica."

4. **NUNCA das diagnósticos ni prescribes tratamientos**: Siempre diriges a consultar profesionales.

📚 CONTEXTO DE LA GUÍA (tu ÚNICA fuente):

{relevant_context}

💬 TU FORMA DE COMUNICARTE:
- Cálida, empática y comprensiva
- Natural y conversacional
- Usa ejemplos simples
- Valida emociones
- Positiva pero realista
- Ocasionalmente usa emojis 💜

✅ ESTRUCTURA DE RESPUESTAS:
1. Empatía/Validación inicial
2. Información del contexto
3. Explicación clara
4. Pasos o sugerencias prácticas
5. Cierre motivador

RECUERDA: Si la pregunta NO es sobre SOP, RECHAZA amablemente y redirige. NO contestes sobre otros temas."""

    return prompt

# Función para simular escritura natural
def stream_with_delay(text, placeholder):
    words = text.split()
    displayed_text = ""
    
    for i, word in enumerate(words):
        displayed_text += word + " "
        
        if word.endswith('.') or word.endswith('?') or word.endswith('!'):
            time.sleep(0.08)
        elif word.endswith(','):
            time.sleep(0.04)
        else:
            time.sleep(0.02)
        
        if i % 3 == 0:
            placeholder.markdown(displayed_text + "▌")
    
    return displayed_text

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_response" not in st.session_state:
    st.session_state.pending_response = None

# Mensaje de bienvenida
if len(st.session_state.messages) == 0:
    welcome = """¡Hola! Me llamo Sofía 💜

Estoy aquí para ayudarte a entender mejor el **Síndrome de Ovario Poliquístico (SOP)** basándome en la guía internacional más reciente.

**Importante:** Solo puedo ayudarte con temas relacionados al SOP. Para otras consultas médicas, por favor consulta con un profesional.

¿Tienes alguna pregunta sobre el SOP? 😊"""
    
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Procesar respuesta pendiente de botón
if st.session_state.pending_response and pdf_chunks:
    prompt_to_process = st.session_state.pending_response
    st.session_state.pending_response = None
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        
        try:
            # Buscar contexto relevante
            relevant_chunks = find_relevant_chunks(prompt_to_process, pdf_chunks, client)
            context = "\n\n".join(relevant_chunks) if relevant_chunks else pdf_content[:8000]
            
            system_prompt = create_prompt(context)
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in st.session_state.messages[-10:]:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            completion = client.chat.completions.create(
                model=model_selector,
                messages=messages,
                temperature=0.6,
                max_tokens=2048,
                stream=False
            )
            
            full_response = completion.choices[0].message.content
            displayed = stream_with_delay(full_response, placeholder)
            placeholder.markdown(displayed)
            
        except Exception as e:
            full_response = f"Disculpa, tuve un error técnico 😅\n\nError: {str(e)}"
            placeholder.markdown(full_response)
    
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# Input usuario
if prompt := st.chat_input("Escribe aquí tu pregunta sobre SOP... 💭"):
    
    if not pdf_chunks:
        st.error("No hay guía cargada")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Buscar chunks relevantes usando RAG simple
            relevant_chunks = find_relevant_chunks(prompt, pdf_chunks, client, top_k=3)
            
            # Si no hay chunks relevantes, usar el inicio del documento
            if not relevant_chunks:
                context = pdf_content[:8000]
            else:
                context = "\n\n".join(relevant_chunks)
            
            system_prompt = create_prompt(context)
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in st.session_state.messages[-10:]:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            completion = client.chat.completions.create(
                model=model_selector,
                messages=messages,
                temperature=0.6,
                max_tokens=2048,
                stream=False
            )
            
            full_response = completion.choices[0].message.content
            displayed = stream_with_delay(full_response, placeholder)
            placeholder.markdown(displayed)
            
        except Exception as e:
            full_response = f"Disculpa, tuve un error técnico 😅\n\nError: {str(e)}"
            placeholder.markdown(full_response)
    
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💜 Importante")
    st.markdown("Solo información sobre SOP. Consulta profesionales para diagnóstico y tratamiento.")

with col2:
    st.markdown("### 📚 Fuente")
    st.markdown("Guía Internacional de Práctica Clínica para SOP (Monash 2023)")

with col3:
    st.markdown("### 🤝 Comunidad")
    st.markdown("Hay profesionales y grupos de apoyo listos para acompañarte 💪")