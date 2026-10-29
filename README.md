# 🚀 Nexus Inclusivo
Plataforma de Reclutamiento Ético con Inteligencia Artificial.

## ✨ Características Principales
- 🧠 **Procesamiento con IA:** Extracción automática de habilidades y redacción de perfiles anónimos (Blind Hiring) usando GPT-4o-mini.
- 🔒 **Privacidad por Diseño:** Los datos sensibles se ocultan. Solo administradores autorizados pueden revelar identidades, quedando todo registrado en logs de auditoría.
- 💬 **Asistente Virtual:** Chatbot integrado con IA para responder consultas sobre la plataforma en tiempo real.
- 📱 **Integración con WhatsApp:** Contacto directo, fluido y profesional con los candidatos.
- 📊 **Estadísticas en Tiempo Real:** Dashboard con métricas reales del sistema.

## 🛠️ Tecnologías Utilizadas
- **Backend:** FastAPI, Python 3.12, SQLAlchemy, PostgreSQL
- **Frontend:** HTML5, CSS3 (Diseño Tech Premium nativo), Vanilla JavaScript
- **Inteligencia Artificial:** OpenAI API (GPT-4o-mini)
- **Despliegue:** Render (Docker)

## 🔗 Demo en Vivo
Puedes probar la plataforma aquí:  
👉 [https://cv-api-1-ps8r.onrender.com](https://cv-api-1-ps8r.onrender.com)

*(Nota: La primera carga puede tardar ~40 segundos mientras el servidor gratuito de Render se activa).*

## 🚀 Cómo ejecutar localmente
1. Clona el repositorio: `git clone https://github.com/techbiz-ia/cv-api.git`
2. Instala las dependencias: `pip install -r requirements.txt`
3. Configura tus variables de entorno en un archivo `.env` (OPENAI_API_KEY, DATABASE_URL, SECRET_KEY).
4. Ejecuta el servidor: `uvicorn main:app --reload`