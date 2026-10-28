   # VERSION FINAL CORREGIDA CON LOGIN Y WHATSAPP
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
    print("✅ Tablas de base de datos verificadas y creadas.")
    yield

app = FastAPI(title="Nexus Inclusivo API", version="2.0.0", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/health")
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
        <title>Nexus Inclusivo | AI-Powered Recruitment</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * { font-family: 'Inter', sans-serif; }
            
            body {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                color: #e0e0e0;
                min-height: 100vh;
            }
            
            .glass-panel {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }
            
            .gradient-text {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .neon-border {
                border: 2px solid transparent;
                background: linear-gradient(#0a0a0a, #0a0a0a) padding-box,
                            linear-gradient(135deg, #667eea, #764ba2, #f093fb) border-box;
            }
            
            .glow-button {
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .glow-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                transition: left 0.5s;
            }
            
            .glow-button:hover::before {
                left: 100%;
            }
            
            .glow-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
            }
            
            .card-hover {
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            
            .card-hover:hover {
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            }
            
            .skill-chip {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
                border: 1px solid rgba(102, 126, 234, 0.3);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slideIn 0.5s ease-out;
            }
            
            .skill-chip:hover {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4));
                transform: scale(1.1) rotate(2deg);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px) scale(0.9);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(40px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes pulse-glow {
                0%, 100% {
                    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
                }
                50% {
                    box-shadow: 0 0 40px rgba(102, 126, 234, 0.8);
                }
            }
            
            .match-badge {
                animation: pulse-glow 2s ease-in-out infinite;
            }
            
            .tab-active {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
                border-bottom: 3px solid #667eea;
                color: #667eea;
                font-weight: 700;
            }
            
            .tab-inactive {
                border-bottom: 3px solid transparent;
                color: #888;
                transition: all 0.3s ease;
            }
            
            .tab-inactive:hover {
                color: #667eea;
                background: rgba(102, 126, 234, 0.1);
            }
            
            .input-dark {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                color: #e0e0e0;
                transition: all 0.3s ease;
            }
            
            .input-dark:focus {
                background: rgba(255, 255, 255, 0.08);
                border-color: #667eea;
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
            }
            
            .input-dark::placeholder {
                color: #666;
            }
            
            .skeleton {
                background: linear-gradient(90deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.05) 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
            }
            
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            
            .icon-glow {
                filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.6));
            }
            
            .fade-in {
                animation: fadeInUp 0.6s ease-out;
            }
            
            .card-enter {
                animation: fadeInUp 0.5s ease-out;
            }
            
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .text-glow {
                text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            }
        </style>
    </head>
    <body>
        <header class="glass-panel border-b border-gray-800 p-6 sticky top-0 z-50">
            <div class="max-w-6xl mx-auto flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="w-12 h-12 gradient-bg rounded-xl flex items-center justify-center icon-glow">
                        <i class="fas fa-brain text-2xl text-white"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-black gradient-text">NEXUS INCLUSIVO</h1>
                        <p class="text-xs text-gray-400 font-medium">AI-Powered Ethical Recruitment</p>
                    </div>
                </div>
                <div id="authStatus" class="hidden items-center space-x-3 glass-panel px-5 py-2 rounded-full">
                    <i class="fas fa-user-shield text-green-400 icon-glow"></i>
                    <span id="userRole" class="font-bold text-sm">Admin</span>
                    <button onclick="logout()" class="ml-3 text-gray-400 hover:text-red-400 transition text-xs font-semibold">
                        <i class="fas fa-sign-out-alt mr-1"></i>Salir
                    </button>
                </div>
            </div>
        </header>

        <main class="max-w-6xl mx-auto p-8 space-y-8">
            <div id="loginSection" class="glass-panel p-10 rounded-3xl neon-border max-w-md mx-auto mt-20 fade-in">
                <div class="text-center mb-8">
                    <div class="w-20 h-20 gradient-bg rounded-2xl flex items-center justify-center mx-auto mb-4 icon-glow">
                        <i class="fas fa-lock text-3xl text-white"></i>
                    </div>
                    <h2 class="text-3xl font-black gradient-text mb-2">Acceso al Sistema</h2>
                    <p class="text-gray-400 text-sm">Ingresa tus credenciales para continuar</p>
                </div>
                <div class="space-y-5">
                    <div>
                        <label class="block text-sm font-bold text-gray-300 mb-2">
                            <i class="fas fa-user mr-2 text-purple-400"></i>Usuario
                        </label>
                        <input type="text" id="loginUser" class="input-dark w-full p-4 rounded-xl outline-none" placeholder="AdminNuevo">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-gray-300 mb-2">
                            <i class="fas fa-key mr-2 text-purple-400"></i>Contraseña
                        </label>
                        <input type="password" id="loginPass" class="input-dark w-full p-4 rounded-xl outline-none" placeholder="••••••••">
                    </div>
                    <button id="loginBtn" onclick="login()" class="glow-button w-full gradient-bg text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-2xl">
                        <i class="fas fa-sign-in-alt mr-2"></i> <span>Ingresar al Sistema</span>
                    </button>
                    <p id="loginError" class="text-red-400 text-sm mt-3 hidden text-center font-semibold"></p>
                </div>
            </div>

            <div id="mainDashboard" class="hidden fade-in">
                <div class="flex space-x-2 mb-8 glass-panel p-2 rounded-2xl">
                    <button id="tab-analyze" onclick="showTab('analyze')" class="tab-active flex-1 px-6 py-4 text-base flex items-center justify-center space-x-3 rounded-xl transition-all">
                        <i class="fas fa-file-alt text-xl"></i> <span class="font-bold">Analizar CV</span>
                    </button>
                    <button id="tab-search" onclick="showTab('search')" class="tab-inactive flex-1 px-6 py-4 text-base flex items-center justify-center space-x-3 rounded-xl transition-all">
                        <i class="fas fa-search text-xl"></i> <span class="font-bold">Buscar Candidatos</span>
                    </button>
                </div>

                <div id="analyzeSection" class="glass-panel p-10 rounded-3xl neon-border">
                    <div class="text-center mb-8">
                        <h2 class="text-3xl font-black gradient-text mb-2">Procesamiento con IA</h2>
                        <p class="text-gray-400">Sube un archivo o pega el texto del currículum</p>
                    </div>
                    <div class="space-y-6">
                        <div class="glass-panel p-6 rounded-2xl">
                            <label class="block text-sm font-bold text-gray-300 mb-3">
                                <i class="fas fa-cloud-upload-alt mr-2 text-purple-400"></i>Opción A: Subir archivo
                            </label>
                            <input type="file" id="cvFile" accept=".pdf,.docx,.txt" class="input-dark w-full p-4 rounded-xl text-sm file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-purple-600 file:text-white hover:file:bg-purple-700 cursor-pointer">
                        </div>
                        <div class="relative flex py-3 items-center">
                            <div class="flex-grow border-t border-gray-700"></div>
                            <span class="flex-shrink-0 mx-4 text-gray-500 text-sm font-bold">O</span>
                            <div class="flex-grow border-t border-gray-700"></div>
                        </div>
                        <div class="glass-panel p-6 rounded-2xl">
                            <label class="block text-sm font-bold text-gray-300 mb-3">
                                <i class="fas fa-paste mr-2 text-purple-400"></i>Opción B: Pegar texto
                            <div class="glass-panel p-6 rounded-2xl">
    <label class="block text-sm font-bold text-gray-300 mb-3">
        <i class="fab fa-whatsapp mr-2 text-green-400"></i>WhatsApp del candidato (opcional)
    </label>
    <input type="text" id="cvWhatsapp" class="input-dark w-full p-4 rounded-xl outline-none" placeholder="+54 9 299 329 3669">
    <p class="text-xs text-gray-500 mt-2">Se mostrará al revelar la identidad</p>
</div>
                            </label>
                            <textarea id="cvText" rows="6" class="input-dark w-full p-4 rounded-xl outline-none text-sm resize-none" placeholder="Pega aquí el contenido del CV..."></textarea>
                        </div>
                    </div>
                    <button id="analyzeBtn" onclick="procesarCV()" class="glow-button mt-8 w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-2xl">
                        <i class="fas fa-magic mr-2"></i> <span>Procesar con IA</span>
                    </button>

                    <div id="resultSection" class="hidden mt-8 space-y-5">
                        <div class="glass-panel p-6 rounded-2xl neon-border">
                            <h3 class="font-black text-xl gradient-text mb-4 flex items-center">
                                <i class="fas fa-bullseye mr-3"></i>Habilidades Detectadas
                            </h3>
                            <div id="skillsContainer" class="flex flex-wrap gap-3"></div>
                        </div>
                        <div id="redactedBox" class="hidden glass-panel p-6 rounded-2xl">
                            <h3 class="font-black text-xl text-gray-200 mb-4 flex items-center">
                                <i class="fas fa-shield-alt mr-3 text-purple-400"></i>Texto Redactado
                            </h3>
                            <p id="redactedText" class="text-sm text-gray-300 italic leading-relaxed"></p>
                        </div>
                    </div>
                    <p id="analyzeError" class="text-red-400 text-sm mt-4 hidden text-center font-semibold"></p>
                </div>

                <div id="searchSection" class="hidden glass-panel p-10 rounded-3xl neon-border">
                    <div class="text-center mb-8">
                        <h2 class="text-3xl font-black gradient-text mb-2">Búsqueda Inteligente</h2>
                        <p class="text-gray-400">Encuentra candidatos con Blind Hiring</p>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div class="md:col-span-2 glass-panel p-6 rounded-2xl">
                            <label class="block text-sm font-bold text-gray-300 mb-3">
                                <i class="fas fa-tags mr-2 text-purple-400"></i>Habilidades requeridas
                            </label>
                            <input type="text" id="searchSkills" class="input-dark w-full p-4 rounded-xl outline-none" placeholder="Python, AWS, Docker, Machine Learning">
                        </div>
                        <div class="glass-panel p-6 rounded-2xl">
                            <label class="block text-sm font-bold text-gray-300 mb-3">
                                <i class="fas fa-percentage mr-2 text-purple-400"></i>Match mínimo
                            </label>
                            <input type="number" id="searchMinMatch" value="50" min="0" max="100" class="input-dark w-full p-4 rounded-xl outline-none">
                        </div>
                    </div>
                    <button onclick="buscarCandidatos()" class="glow-button w-full gradient-bg text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-2xl">
                        <i class="fas fa-search mr-2"></i> <span>Buscar Candidatos</span>
                    </button>
                    <div id="searchResults" class="hidden mt-8 space-y-6"></div>
                    <p id="searchError" class="text-red-400 text-sm mt-4 hidden text-center font-semibold"></p>
                </div>
            </div>
        </main>
        <footer class="text-center p-8 text-gray-500 text-sm font-medium">
            <p>&copy; 2026 Nexus Inclusivo. Powered by AI & Ethical Design.</p>
        </footer>

        <script>
            let token = "";
            const API_URL = "https://cv-api-1-ps8r.onrender.com";

            function showTab(tabName) {
                document.getElementById('analyzeSection').classList.add('hidden');
                document.getElementById('searchSection').classList.add('hidden');
                document.getElementById('tab-analyze').className = "tab-inactive flex-1 px-6 py-4 text-base flex items-center justify-center space-x-3 rounded-xl transition-all";
                document.getElementById('tab-search').className = "tab-inactive flex-1 px-6 py-4 text-base flex items-center justify-center space-x-3 rounded-xl transition-all";
                document.getElementById(tabName + 'Section').classList.remove('hidden');
                document.getElementById('tab-' + tabName).className = "tab-active flex-1 px-6 py-4 text-base flex items-center justify-center space-x-3 rounded-xl transition-all";
            }

            async function login() {
                const user = document.getElementById('loginUser').value;
                const pass = document.getElementById('loginPass').value;
                const errorDiv = document.getElementById('loginError');
                const loginBtn = document.getElementById('loginBtn');

                if (!user || !pass) {
                    errorDiv.textContent = "Por favor completa todos los campos.";
                    errorDiv.classList.remove('hidden');
                    return;
                }

                loginBtn.disabled = true;
                loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Conectando...';
                errorDiv.classList.add('hidden');

                const formData = new URLSearchParams();
                formData.append('username', user);
                formData.append('password', pass);

                try {
                    const response = await fetch(API_URL + '/usuarios/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.detail || "Credenciales incorrectas");
                    }
                    
                    const data = await response.json();
                    token = data.access_token;
                    
                    let rol = "User";
                    try {
                        const payload = JSON.parse(atob(token.split('.')[1]));
                        rol = payload.rol || "User";
                    } catch (e) {}
                    
                    document.getElementById('userRole').textContent = rol;
                    document.getElementById('loginSection').classList.add('hidden');
                    document.getElementById('mainDashboard').classList.remove('hidden');
                    document.getElementById('authStatus').classList.remove('hidden');
                    document.getElementById('authStatus').classList.add('flex');
                    
                } catch (err) {
                    errorDiv.textContent = "❌ " + err.message;
                    errorDiv.classList.remove('hidden');
                    loginBtn.disabled = false;
                    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i> Ingresar al Sistema';
                }
            }

            function logout() {
                token = "";
                document.getElementById('loginSection').classList.remove('hidden');
                document.getElementById('mainDashboard').classList.add('hidden');
                document.getElementById('authStatus').classList.add('hidden');
            }

            async function procesarCV() {
    // ... (código existente)
    
    const whatsappInput = document.getElementById('cvWhatsapp');
    const whatsapp = whatsappInput.value.trim();
    
    // ... (validación existente)
    
    try {
        let response;
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('whatsapp', whatsapp);  // 🔥 Agregar WhatsApp
            response = await fetch(API_URL + '/cvs/procesar-archivo', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + token },
                body: formData
            });
        } else {
            response = await fetch(API_URL + '/cvs/procesar-ia', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                body: JSON.stringify({ texto_cv: texto, whatsapp: whatsapp })  // 🔥 Agregar WhatsApp
            });
        }
        // ... (resto del código igual)
    }
}
            async function buscarCandidatos() {
                const skillsInput = document.getElementById('searchSkills').value;
                const minMatch = parseInt(document.getElementById('searchMinMatch').value) || 50;
                const errorDiv = document.getElementById('searchError');
                const resultsDiv = document.getElementById('searchResults');
                
                if (!skillsInput.trim()) {
                    errorDiv.textContent = "Ingresa al menos una habilidad.";
                    errorDiv.classList.remove('hidden');
                    return;
                }

                const skillsArray = skillsInput.split(',').map(function(s) { return s.trim(); }).filter(function(s) { return s.length > 0; });
                
                let esAdmin = false;
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    esAdmin = (payload.rol === "Admin");
                } catch (e) {}
                
                resultsDiv.innerHTML = '<div class="space-y-4"><div class="skeleton h-40 w-full rounded-2xl"></div><div class="skeleton h-40 w-full rounded-2xl"></div></div>';
                resultsDiv.classList.remove('hidden');
                errorDiv.classList.add('hidden');

                try {
                    const response = await fetch(API_URL + '/cvs/buscar-candidatos', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                        body: JSON.stringify({ skills_requeridas: skillsArray, min_match_porcentaje: minMatch })
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Error al buscar");

                    resultsDiv.innerHTML = ""; 
                    if (data.total_encontrados === 0) {
                        resultsDiv.innerHTML = '<p class="text-center text-gray-500 py-12 text-lg">No se encontraron candidatos con esos requisitos.</p>';
                        return;
                    }

                  data.candidatos.forEach(function(candidato, index) {
    // ... (código existente)
    
    // 🔥 Agregar botón de WhatsApp si existe
    const whatsappButton = candidato.whatsapp 
        ? '<a href="https://wa.me/' + candidato.whatsapp.replace(/[^0-9]/g, '') + '" target="_blank" class="glow-button bg-green-600 hover:bg-green-700 text-white text-sm font-bold px-6 py-3 rounded-xl transition-all shadow-xl inline-flex items-center"><i class="fab fa-whatsapp mr-2 text-xl"></i> Contactar por WhatsApp</a>'
        : '';
    
    // ... (resto del código de la tarjeta)
    
    // 🔥 Agregar el botón de WhatsApp antes del botón de revelar identidad
    card.innerHTML = 
        // ... (HTML existente)
        '<div class="flex items-center justify-between border-t border-gray-700 pt-4 space-x-3">' +
            '<span class="text-xs text-gray-500 font-bold"><i class="fas fa-user-shield mr-1"></i> Privacidad protegida</span>' +
            '<div class="flex space-x-2">' +
                whatsappButton +
                adminButton +
            '</div>' +
        '</div>' +
        // ... (resto del HTML)
});
                } catch (err) {
                    resultsDiv.classList.add('hidden');
                    errorDiv.textContent = "❌ " + err.message;
                    errorDiv.classList.remove('hidden');
                }
            }

            async function revelarIdentidad(perfilId, boton) {
                const contenedor = boton.closest('.glass-panel').querySelector('.identity-box');
                contenedor.classList.remove('hidden');
                contenedor.innerHTML = '<p class="text-sm text-purple-400 font-bold"><i class="fas fa-spinner fa-spin mr-2"></i> Verificando permisos...</p>';

                try {
                    const response = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(perfilId) + '/identidad', {
                        method: 'GET',
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Acceso denegado");

                    contenedor.innerHTML = 
                        '<h5 class="text-xl font-black gradient-text mb-4 flex items-center"><i class="fas fa-unlock mr-3"></i> Identidad Revelada</h5>' +
                        '<p class="text-xs text-gray-400 mb-4 font-bold">Auditado por: <strong class="text-purple-400">' + data.identidad_revelada_por + '</strong></p>' +
                        '<pre class="text-xs text-gray-300 whitespace-pre-wrap bg-black bg-opacity-30 p-5 rounded-xl border border-gray-700 leading-relaxed">' + data.texto_original_completo + '</pre>';
                    
                    boton.disabled = true;
                    boton.innerHTML = '<i class="fas fa-check mr-2"></i> Revelado';
                    boton.className = 'bg-green-600 text-white text-sm font-bold px-6 py-3 rounded-xl shadow-xl cursor-not-allowed';
                } catch (err) {
                    contenedor.innerHTML = '<p class="text-sm text-red-400 font-bold">🔒 ' + err.message + '</p>';
                }
            }
        </script>
   <!-- Botón flotante de WhatsApp -->
<div class="fixed bottom-8 right-8 z-50">
    <a href="https://wa.me/5492993293669?text=Hola%2C%20quiero%20más%20información%20sobre%20Nexus%20Inclusivo" 
       target="_blank" 
       class="glow-button bg-green-500 hover:bg-green-600 text-white w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-all hover:scale-110">
        <i class="fab fa-whatsapp text-3xl"></i>
    </a>
    <div class="absolute bottom-20 right-0 glass-panel p-3 rounded-xl text-xs text-gray-300 whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity">
        💬 ¿Necesitas ayuda?
    </div>
</div>
     </body>
    </html>
    """