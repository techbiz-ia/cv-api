from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.database import Base, engine
from app.routers import usuarios, cvs
import app.models.usuarios
import app.models.cv
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas.")
    yield
app = FastAPI(title="Nexus Inclusivo API", version="7.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cv-api-1-ps8r.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/health")
@app.get("/migrate-db")
def migrate_db():
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN whatsapp VARCHAR;"))
            conn.commit()
        return {"mensaje": "✅ Columna 'whatsapp' agregada exitosamente a la base de datos."}
    except Exception as e:
        return {"mensaje": f"ℹ️ La columna probablemente ya existe o hubo un detalle: {str(e)}"}
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>Nexus Inclusivo · Reclutamiento del Futuro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --accent: #6366f1;
            --accent-light: #818cf8;
            --success: #10b981;
            --whatsapp: #25D366;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: #f1f5f9;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Partículas animadas */
        .particles {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        
        .particle {
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(99, 102, 241, 0.5);
            border-radius: 50%;
            animation: float 15s infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) translateX(50px); opacity: 0; }
        }
        
        /* Header */
        .header {
            background: rgba(18, 18, 26, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
            position: relative;
            z-index: 1;
        }
        
        .flex { display: flex; align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-3 { gap: 12px; }
        
        .logo {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.5); }
            50% { box-shadow: 0 0 50px rgba(99, 102, 241, 0.8); }
        }
        
        .logo i { color: white; font-size: 24px; }
        
        .brand-title {
            font-size: 24px;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200% 200%;
            animation: gradient-shift 3s ease infinite;
        }
        
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .brand-subtitle {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 2px;
        }
        
        .user-badge {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 10px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        
        .user-badge i { color: var(--success); }
        
        .btn-logout {
            background: transparent;
            border: 1px solid rgba(148, 163, 184, 0.3);
            color: #94a3b8;
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.5);
            color: #f87171;
        }
        
        /* Hero Section */
        .hero {
            text-align: center;
            padding: 80px 0 60px;
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .hero-title {
            font-size: 56px;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            letter-spacing: -2px;
            line-height: 1.1;
        }
        
        .hero-subtitle {
            font-size: 20px;
            color: #94a3b8;
            margin-bottom: 40px;
            font-weight: 400;
        }
        
        .typing-text {
            font-size: 18px;
            color: var(--accent-light);
            font-weight: 600;
            min-height: 30px;
        }
        
        .typing-text::after {
            content: '|';
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        /* Stats */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin: 60px 0;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            transition: all 0.3s;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .stat-card:hover {
            transform: translateY(-8px);
            border-color: var(--accent);
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
        }
        
        .stat-number {
            font-size: 48px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent), var(--accent-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #94a3b8;
            font-weight: 500;
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 40px;
            margin-top: 32px;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .card-title {
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #f1f5f9;
        }
        
        .card-subtitle {
            font-size: 15px;
            color: #94a3b8;
            margin-bottom: 32px;
        }
        
        /* Inputs */
        .field-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 10px;
        }
        
        .input {
            width: 100%;
            padding: 14px 18px;
            background: var(--bg-primary);
            border: 2px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            color: #f1f5f9;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
            margin-bottom: 24px;
        }
        
        .input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        }
        
        /* Buttons */
        .btn {
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            border: none;
            color: white;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .btn:hover::before { width: 400px; height: 400px; }
        .btn:hover { transform: translateY(-3px); }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #10b981, #059669);
            box-shadow: 0 8px 30px rgba(16, 185, 129, 0.4);
        }
        
        .btn-sm {
            padding: 10px 20px;
            font-size: 14px;
            width: auto;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 32px;
        }
        
        .tab {
            flex: 1;
            padding: 16px 24px;
            background: var(--bg-card);
            border: 2px solid rgba(99, 102, 241, 0.2);
            color: #94a3b8;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            border-radius: 12px;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        }
        
        /* Utilities */
        .hidden { display: none !important; }
        .text-center { text-align: center; }
        .text-muted { color: #94a3b8; }
        .text-error { color: #ef4444; }
        .mb-6 { margin-bottom: 24px; }
        .mt-6 { margin-top: 24px; }
        
        /* Candidate cards */
        .candidate {
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 32px;
            margin-top: 24px;
            transition: all 0.3s;
        }
        
        .candidate:hover {
            transform: translateY(-6px);
            border-color: var(--accent);
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.2);
        }
        
        .match-badge {
            background: rgba(16, 185, 129, 0.2);
            border: 2px solid rgba(16, 185, 129, 0.4);
            color: var(--success);
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 700;
        }
        
        .skill-tag {
            display: inline-block;
            padding: 8px 14px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            color: var(--accent-light);
            margin: 4px;
        }
        
        /* Chat Widget */
        .chat-widget {
            position: fixed;
            bottom: 28px;
            left: 28px;
            z-index: 1000;
        }
        
        .chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5);
            transition: all 0.3s;
        }
        
        .chat-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.7);
        }
        
        .chat-box {
            position: absolute;
            bottom: 80px;
            left: 0;
            width: 380px;
            height: 500px;
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            display: none;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        
        .chat-box.active { display: flex; }
        
        .chat-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 20px 20px 0 0;
            color: white;
            font-weight: 700;
            font-size: 16px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .chat-message {
            margin-bottom: 16px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-message.user {
            text-align: right;
        }
        
        .chat-bubble {
            display: inline-block;
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 80%;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .chat-message.bot .chat-bubble {
            background: var(--bg-secondary);
            color: #f1f5f9;
            border-bottom-left-radius: 4px;
        }
        
        .chat-message.user .chat-bubble {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .chat-input-area {
            padding: 16px;
            border-top: 1px solid rgba(99, 102, 241, 0.2);
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            background: var(--bg-primary);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 10px;
            color: #f1f5f9;
            font-size: 14px;
            outline: none;
        }
        
        .chat-send {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            font-weight: 600;
        }
        
        /* WhatsApp float */
        .wa-float {
            position: fixed;
            bottom: 28px;
            right: 28px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--whatsapp);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            box-shadow: 0 8px 30px rgba(37, 211, 102, 0.5);
            z-index: 999;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .wa-float:hover {
            transform: scale(1.1);
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>
    
    <header class="header">
        <div class="container flex justify-between">
            <div class="flex gap-3">
                <div class="logo">
                    <i class="fas fa-brain"></i>
                </div>
                <div>
                    <div class="brand-title">Nexus Inclusivo</div>
                    <div class="brand-subtitle">Reclutamiento del Futuro</div>
                </div>
            </div>
            <div id="authStatus" class="hidden flex gap-3">
                <div class="user-badge">
                    <i class="fas fa-shield-alt"></i>
                    <span id="userRole">Admin</span>
                </div>
                <button class="btn-logout" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Cerrar sesión
                </button>
            </div>
        </div>
    </header>

    <main class="container">
        <section id="loginSection">
            <div class="hero">
                <h1 class="hero-title">Reclutamiento<br>del Futuro</h1>
                <p class="hero-subtitle">Potenciado por Inteligencia Artificial</p>
                <div class="typing-text" id="typingText"></div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Ético y Privado</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">IA</div>
                    <div class="stat-label">Procesamiento Inteligente</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Disponibilidad Total</div>
                </div>
            </div>
            
            <div class="card" style="max-width:450px;margin:0 auto;">
                <h2 class="card-title text-center">Iniciar sesión</h2>
                <p class="card-subtitle text-center">Accede a tu cuenta</p>
                <label class="field-label">Usuario</label>
                <input id="loginUser" class="input" placeholder="tu.usuario">
                <label class="field-label">Contraseña</label>
                <input id="loginPass" class="input" type="password" placeholder="••••••••">
                <button id="loginBtn" class="btn btn-primary" onclick="login()" style="margin-top:12px;">
                    Ingresar al sistema
                </button>
                <p id="loginError" class="hidden text-error mt-6 text-center"></p>
            </div>
        </section>

        <section id="dashboard" class="hidden">
            <div class="tabs">
                <button id="tab-analyze" class="tab active" onclick="showTab('analyze')">
                    <i class="fas fa-file-alt"></i> Analizar CV
                </button>
                <button id="tab-search" class="tab" onclick="showTab('search')">
                    <i class="fas fa-search"></i> Buscar candidatos
                </button>
            </div>

            <div id="analyzeSection" class="card">
                <h2 class="card-title">Procesamiento de currículum</h2>
                <p class="card-subtitle">Analiza un CV con inteligencia artificial</p>
                
                <label class="field-label"><i class="fas fa-file-upload"></i> Archivo (PDF, DOCX, TXT)</label>
                <input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="input">
                
                <label class="field-label"><i class="fab fa-whatsapp"></i> WhatsApp del candidato (opcional)</label>
                <input id="cvWhatsapp" class="input" placeholder="">
                <p class="text-muted" style="font-size:12px;margin-top:-18px;margin-bottom:24px;">
                    Solo visible para administradores
                </p>
                
                <label class="field-label"><i class="fas fa-paste"></i> Texto del currículum</label>
                <textarea id="cvText" rows="6" class="input" style="resize:vertical;" placeholder="Pega aquí el contenido del CV..."></textarea>
                
                <button id="analyzeBtn" class="btn btn-success" onclick="procesarCV()">
                    <i class="fas fa-magic"></i> Procesar con IA
                </button>
                <p id="analyzeError" class="hidden text-error mt-6 text-center"></p>
                <div id="analyzeResult" class="hidden mt-6 text-center"></div>
            </div>

            <div id="searchSection" class="card hidden">
                <h2 class="card-title">Búsqueda de candidatos</h2>
                <p class="card-subtitle">Encuentra profesionales con Blind Hiring</p>
                
                <label class="field-label"><i class="fas fa-tags"></i> Habilidades requeridas</label>
                <input id="searchSkills" class="input" placeholder="Python, FastAPI, AWS">
                
                <label class="field-label"><i class="fas fa-percent"></i> Coincidencia mínima (%)</label>
                <input id="searchMinMatch" type="number" value="50" class="input">
                
                <button class="btn btn-primary" onclick="buscarCandidatos()">
                    <i class="fas fa-search"></i> Buscar candidatos
                </button>
                <p id="searchError" class="hidden text-error mt-6 text-center"></p>
                <div id="searchResults" class="mt-6"></div>
            </div>
        </section>
    </main>

    <!-- Chat Widget -->
    <div class="chat-widget">
        <button class="chat-toggle" onclick="toggleChat()">
            <i class="fas fa-comments"></i>
        </button>
        <div class="chat-box" id="chatBox">
            <div class="chat-header">
                <i class="fas fa-robot"></i> Asistente Virtual
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="chat-message bot">
                    <div class="chat-bubble">¡Hola! 👋 Soy el asistente de Nexus Inclusivo. ¿En qué puedo ayudarte?</div>
                </div>
            </div>
            <div class="chat-input-area">
                <input id="chatInput" class="chat-input" placeholder="Escribe tu consulta..." onkeypress="if(event.key==='Enter')sendChat()">
                <button class="chat-send" onclick="sendChat()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <a class="wa-float" href="https://wa.me/5492993293669" target="_blank">
        <i class="fab fa-whatsapp"></i>
    </a>

    <script>
        // Partículas
        const particlesContainer = document.getElementById('particles');
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particlesContainer.appendChild(particle);
        }

        // Typing animation
        const texts = [
            'Procesamiento ético con IA',
            'Blind Hiring garantizado',
            'Búsqueda inteligente de talento',
            'Privacidad por diseño'
        ];
        let textIndex = 0;
        let charIndex = 0;
        const typingElement = document.getElementById('typingText');

        function typeText() {
            if (charIndex < texts[textIndex].length) {
                typingElement.textContent += texts[textIndex].charAt(charIndex);
                charIndex++;
                setTimeout(typeText, 50);
            } else {
                setTimeout(eraseText, 2000);
            }
        }

        function eraseText() {
            if (charIndex > 0) {
                typingElement.textContent = texts[textIndex].substring(0, charIndex - 1);
                charIndex--;
                setTimeout(eraseText, 30);
            } else {
                textIndex = (textIndex + 1) % texts.length;
                setTimeout(typeText, 500);
            }
        }

        typeText();

        // Chat
        function toggleChat() {
            document.getElementById('chatBox').classList.toggle('active');
        }

                async function sendChat() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;

            const messagesContainer = document.getElementById('chatMessages');
            
            messagesContainer.innerHTML += `<div class="chat-message user"><div class="chat-bubble">${message}</div></div>`;
            input.value = '';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            messagesContainer.innerHTML += `<div class="chat-message bot" id="typing"><div class="chat-bubble"><i class="fas fa-spinner fa-spin"></i> Pensando...</div></div>`;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            try {
                const headers = { 'Content-Type': 'application/json' };
                
                if (token) {
                    headers['Authorization'] = 'Bearer ' + token;
                }

                const res = await fetch(API_URL + '/chat/ask', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ message: message })
                });

                if (res.status === 401) {
                    document.getElementById('typing').remove();
                    messagesContainer.innerHTML += `<div class="chat-message bot"><div class="chat-bubble">🔒 Por seguridad, debes <strong>iniciar sesión</strong> para usar el asistente virtual.</div></div>`;
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    return;
                }

                const data = await res.json();
                
                document.getElementById('typing').remove();
                messagesContainer.innerHTML += `<div class="chat-message bot"><div class="chat-bubble">${data.response}</div></div>`;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } catch (e) {
                document.getElementById('typing').remove();
                messagesContainer.innerHTML += `<div class="chat-message bot"><div class="chat-bubble">Lo siento, hubo un error de conexión. Intenta de nuevo.</div></div>`;
            }
        }

        var token = "";
        var API_URL = "https://cv-api-1-ps8r.onrender.com";

        function showTab(name) {
            document.getElementById('analyzeSection').classList.add('hidden');
            document.getElementById('searchSection').classList.add('hidden');
            document.getElementById(name + 'Section').classList.remove('hidden');
            document.getElementById('tab-analyze').className = name === 'analyze' ? 'tab active' : 'tab';
            document.getElementById('tab-search').className = name === 'search' ? 'tab active' : 'tab';
        }

        function getRole() {
            try { return JSON.parse(atob(token.split('.')[1])).rol || 'User'; }
            catch (e) { return 'User'; }
        }

        async function login() {
            var user = document.getElementById('loginUser').value;
            var pass = document.getElementById('loginPass').value;
            var err = document.getElementById('loginError');
            var btn = document.getElementById('loginBtn');
            err.classList.add('hidden');
            if (!user || !pass) {
                err.textContent = 'Completa todos los campos.';
                err.classList.remove('hidden');
                return;
            }
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Conectando...';
            var body = new URLSearchParams();
            body.append('username', user);
            body.append('password', pass);
            try {
                var res = await fetch(API_URL + '/usuarios/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: body
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Credenciales incorrectas');
                token = data.access_token;
                document.getElementById('userRole').textContent = getRole();
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('dashboard').classList.remove('hidden');
                document.getElementById('authStatus').classList.remove('hidden');
            } catch (e) {
                err.textContent = String(e.message);
                err.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Ingresar al sistema';
            }
        }

        function logout() {
            token = "";
            document.getElementById('loginSection').classList.remove('hidden');
            document.getElementById('dashboard').classList.add('hidden');
            document.getElementById('authStatus').classList.add('hidden');
        }

        async function procesarCV() {
        if (file && file.size > 5 * 1024 * 1024) { // 5 MB
    err.textContent = 'El archivo es demasiado grande. Máximo 5MB.';
    err.classList.remove('hidden');
    return;
}
            var file = document.getElementById('cvFile').files[0];
            var texto = document.getElementById('cvText').value.trim();
            var whatsapp = document.getElementById('cvWhatsapp').value.trim();
            var btn = document.getElementById('analyzeBtn');
            var err = document.getElementById('analyzeError');
            var out = document.getElementById('analyzeResult');
            err.classList.add('hidden');
            out.classList.add('hidden');
            if (!file && !texto) {
                err.textContent = 'Sube un archivo o pega el texto.';
                err.classList.remove('hidden');
                return;
            }
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            try {
                var res;
                if (file) {
                    var fd = new FormData();
                    fd.append('file', file);
                    fd.append('whatsapp', whatsapp);
                    res = await fetch(API_URL + '/cvs/procesar-archivo', {
                        method: 'POST',
                        headers: { 'Authorization': 'Bearer ' + token },
                        body: fd
                    });
                } else {
                    res = await fetch(API_URL + '/cvs/procesar-ia', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                        body: JSON.stringify({ texto_cv: texto, whatsapp: whatsapp })
                    });
                }
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al procesar');
                out.textContent = data.status === 'pendiente' ? 'Archivo recibido. Procesando...' : 'CV procesado correctamente.';
                out.classList.remove('hidden');
            } catch (e) {
                err.textContent = String(e.message);
                err.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-magic"></i> Procesar con IA';
            }
        }

        async function buscarCandidatos() {
            var raw = document.getElementById('searchSkills').value;
            var min = parseInt(document.getElementById('searchMinMatch').value) || 50;
            var err = document.getElementById('searchError');
            var box = document.getElementById('searchResults');
            err.classList.add('hidden');
            if (!raw.trim()) {
                err.textContent = 'Ingresa al menos una habilidad.';
                err.classList.remove('hidden');
                return;
            }
            var skills = raw.split(',').map(function (s) { return s.trim(); }).filter(function (s) { return s.length; });
            box.innerHTML = '<p class="text-muted mt-6 text-center"><i class="fas fa-spinner fa-spin"></i> Buscando...</p>';
            try {
                var res = await fetch(API_URL + '/cvs/buscar-candidatos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ skills_requeridas: skills, min_match_porcentaje: min })
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al buscar');
                box.innerHTML = '';
                if (!data.total_encontrados) {
                    box.innerHTML = '<p class="text-muted mt-6 text-center">No se encontraron candidatos.</p>';
                    return;
                }
                var admin = getRole() === 'Admin';
                data.candidatos.forEach(function (c) {
                    var card = document.createElement('div');
                    card.className = 'candidate';
                    
                    var skillsHtml = (c.skills_coincidentes || []).map(function (s) {
                        return '<span class="skill-tag">' + s + '</span>';
                    }).join('');
                    
                    var waBtn = c.whatsapp ? '<a class="btn btn-sm" style="background:var(--whatsapp);" target="_blank" href="https://wa.me/' + c.whatsapp.replace(/[^0-9]/g, '') + '"><i class="fab fa-whatsapp"></i> WhatsApp</a>' : '';
                    var revealBtn = admin ? '<button class="btn btn-sm btn-primary reveal-btn"><i class="fas fa-unlock"></i> Revelar identidad</button>' : '';
                    
                    card.innerHTML =
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">' +
                            '<div style="font-size:18px;font-weight:700;">' + c.perfil_ciego_id + '</div>' +
                            '<span class="match-badge">' + c.match_porcentaje + '% match</span>' +
                        '</div>' +
                        '<div style="margin-bottom:20px;">' + skillsHtml + '</div>' +
                        '<div style="background:var(--bg-primary);padding:16px;border-radius:10px;font-style:italic;color:#94a3b8;">' + (c.cv_redactado || 'Sin perfil') + '</div>' +
                        '<div style="display:flex;gap:10px;margin-top:20px;">' + waBtn + revealBtn + '</div>' +
                        '<div class="hidden identity-box"></div>';
                    box.appendChild(card);
                    
                    var rb = card.querySelector('.reveal-btn');
                    if (rb) {
                        rb.addEventListener('click', function () { revelarIdentidad(c.perfil_ciego_id, rb, card); });
                    }
                });
            } catch (e) {
                err.textContent = String(e.message);
                err.classList.remove('hidden');
            }
        }

        async function revelarIdentidad(id, btn, card) {
            var box = card.querySelector('.identity-box');
            box.classList.remove('hidden');
            box.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Verificando...</p>';
            try {
                var res = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(id) + '/identidad', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Acceso denegado');
                
                var html = '<p style="color:var(--accent-light);font-weight:600;">Revelado por: ' + data.identidad_revelada_por + '</p>';
                if (data.whatsapp) {
                    html += '<p style="color:var(--success);"><i class="fab fa-whatsapp"></i> ' + data.whatsapp + '</p>';
                }
                html += '<pre style="white-space:pre-wrap;color:#cbd5e1;background:var(--bg-secondary);padding:16px;border-radius:10px;margin-top:12px;">' + data.texto_original_completo + '</pre>';
                
                box.innerHTML = html;
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-check"></i> Revelado';
            } catch (e) {
                box.innerHTML = '<p style="color:#ef4444;">Error: ' + String(e.message) + '</p>';
            }
        }
    </script>
</body>
</html>
"""