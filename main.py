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

app = FastAPI(title="Nexus Inclusivo API", version="1.0.0", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")
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
        <title>Nexus Inclusivo | Reclutamiento con IA</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { 
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .glass-panel { 
                background: rgba(255, 255, 255, 0.98); 
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .skill-tag { 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                animation: fadeInUp 0.4s ease-out;
            }
            .skill-tag:hover { 
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }
            .tab-active { 
                border-bottom: 3px solid #2563eb; 
                color: #2563eb; 
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .tab-inactive { 
                border-bottom: 3px solid transparent; 
                color: #6b7280;
                transition: all 0.3s ease;
            }
            .tab-inactive:hover { 
                color: #374151;
                transform: translateY(-2px);
            }
            .card-enter {
                animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .btn-primary {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.5);
            }
            .btn-primary:active {
                transform: translateY(0);
            }
            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            .fade-in {
                animation: fadeIn 0.6s ease-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            input:focus, textarea:focus {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px -2px rgba(37, 99, 235, 0.2);
            }
            .match-badge {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: .8; }
            }
        </style>
    </head>
    <body class="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen font-sans text-gray-800">
        <header class="gradient-bg text-white p-6 shadow-lg">
            <div class="max-w-5xl mx-auto flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-brain text-3xl animate-pulse"></i>
                    <div>
                        <h1 class="text-2xl font-bold">Nexus Inclusivo</h1>
                        <p class="text-blue-100 text-sm">Reclutamiento Inteligente y Ético con IA</p>
                    </div>
                </div>
                <div id="authStatus" class="hidden items-center space-x-2 bg-blue-800 px-4 py-2 rounded-full text-sm shadow-lg">
                    <i class="fas fa-user-shield text-green-400"></i>
                    <span id="userRole" class="font-semibold">Sesión Activa</span>
                    <button onclick="logout()" class="ml-3 text-blue-200 hover:text-white underline text-xs transition">Salir</button>
                </div>
            </div>
        </header>

        <main class="max-w-5xl mx-auto p-6 space-y-6">
            <div id="loginSection" class="glass-panel p-8 rounded-2xl shadow-2xl border border-gray-200 max-w-md mx-auto mt-10 fade-in">
                <h2 class="text-2xl font-bold mb-6 flex items-center text-gray-800">
                    <i class="fas fa-lock mr-3 text-blue-600"></i> Iniciar Sesión
                </h2>
                <div class="space-y-5">
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Usuario</label>
                        <input type="text" id="loginUser" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" placeholder="Ej: AdminNuevo">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Contraseña</label>
                        <input type="password" id="loginPass" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" placeholder="••••••••">
                    </div>
                    <button id="loginBtn" onclick="login()" class="btn-primary w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-lg">
                        <i class="fas fa-sign-in-alt mr-2"></i> <span>Ingresar al Sistema</span>
                    </button>
                    <p id="loginError" class="text-red-500 text-sm mt-3 hidden text-center font-medium"></p>
                </div>
            </div>

            <div id="mainDashboard" class="hidden fade-in">
                <div class="flex border-b-2 border-gray-200 mb-8 space-x-2">
                    <button id="tab-analyze" onclick="showTab('analyze')" class="tab-active px-8 py-4 text-lg flex items-center space-x-3 rounded-t-xl">
                        <i class="fas fa-file-alt text-xl"></i> <span class="font-semibold">Analizar Nuevo CV</span>
                    </button>
                    <button id="tab-search" onclick="showTab('search')" class="tab-inactive px-8 py-4 text-lg flex items-center space-x-3 rounded-t-xl">
                        <i class="fas fa-search text-xl"></i> <span class="font-semibold">Buscar Candidatos</span>
                    </button>
                </div>

                <div id="analyzeSection" class="glass-panel p-8 rounded-2xl shadow-xl border border-gray-200">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Procesar Currículum con IA</h2>
                    <div class="space-y-6">
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-3">
                                <i class="fas fa-upload mr-2 text-blue-600"></i>Opción A: Subir archivo (PDF, DOCX, TXT)
                            </label>
                            <input type="file" id="cvFile" accept=".pdf,.docx,.txt" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-all cursor-pointer">
                        </div>
                        <div class="relative flex py-3 items-center">
                            <div class="flex-grow border-t-2 border-gray-200"></div>
                            <span class="flex-shrink-0 mx-4 text-gray-400 text-sm font-medium">O pega el texto</span>
                            <div class="flex-grow border-t-2 border-gray-200"></div>
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-3">
                                <i class="fas fa-paste mr-2 text-blue-600"></i>Opción B: Pegar texto del CV
                            </label>
                            <textarea id="cvText" rows="6" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm transition-all resize-none" placeholder="Ej: Ingeniero de Software con 4 años de experiencia..."></textarea>
                        </div>
                    </div>
                    <button id="analyzeBtn" onclick="procesarCV()" class="btn-primary mt-6 w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-lg">
                        <i class="fas fa-magic mr-2"></i> <span>Procesar con IA</span>
                    </button>

                    <div id="resultSection" class="hidden mt-8 space-y-4">
                        <div class="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border-2 border-blue-200 shadow-md">
                            <h3 class="font-bold text-blue-900 mb-3 text-lg flex items-center">
                                <i class="fas fa-bullseye mr-2"></i>🎯 Resultado:
                            </h3>
                            <div id="skillsContainer" class="flex flex-wrap gap-3"></div>
                        </div>
                        <div id="redactedBox" class="hidden bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border-2 border-gray-200 shadow-md">
                            <h3 class="font-bold text-gray-800 mb-3 text-lg flex items-center">
                                <i class="fas fa-shield-alt mr-2 text-gray-600"></i>🔒 Texto Redactado:
                            </h3>
                            <p id="redactedText" class="text-sm text-gray-700 italic leading-relaxed"></p>
                        </div>
                    </div>
                    <p id="analyzeError" class="text-red-500 text-sm mt-4 hidden text-center font-medium"></p>
                </div>

                <div id="searchSection" class="hidden glass-panel p-8 rounded-2xl shadow-xl border border-gray-200">
                    <h2 class="text-2xl font-bold mb-6 text-gray-800">Búsqueda de Candidatos (Blind Hiring)</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div class="md:col-span-2">
                            <label class="block text-sm font-semibold text-gray-700 mb-3">
                                <i class="fas fa-tags mr-2 text-purple-600"></i>Habilidades requeridas (separadas por coma)
                            </label>
                            <input type="text" id="searchSkills" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition-all" placeholder="Ej: Python, AWS, Docker">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-3">
                                <i class="fas fa-percentage mr-2 text-purple-600"></i>Coincidencia mínima (%)
                            </label>
                            <input type="number" id="searchMinMatch" value="50" min="0" max="100" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition-all">
                        </div>
                    </div>
                    <button onclick="buscarCandidatos()" class="btn-primary w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-lg">
                        <i class="fas fa-search mr-2"></i> <span>Buscar Candidatos</span>
                    </button>
                    <div id="searchResults" class="hidden mt-8 space-y-5"></div>
                    <p id="searchError" class="text-red-500 text-sm mt-4 hidden text-center font-medium"></p>
                </div>
            </div>
        </main>
        <footer class="text-center p-8 text-gray-500 text-sm font-medium">&copy; 2026 Nexus Inclusivo Core. Potenciado por IA.</footer>

        <script>
            let token = "";
            const API_URL = "https://cv-api-1-ps8r.onrender.com";

            function showTab(tabName) {
                document.getElementById('analyzeSection').classList.add('hidden');
                document.getElementById('searchSection').classList.add('hidden');
                document.getElementById('tab-analyze').className = "tab-inactive px-8 py-4 text-lg flex items-center space-x-3 rounded-t-xl";
                document.getElementById('tab-search').className = "tab-inactive px-8 py-4 text-lg flex items-center space-x-3 rounded-t-xl";
                document.getElementById(tabName + 'Section').classList.remove('hidden');
                document.getElementById('tab-' + tabName).className = "tab-active px-8 py-4 text-lg flex items-center space-x-3 rounded-t-xl";
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
                loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Despertando servidor (espera ~50 seg)...';
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
                const fileInput = document.getElementById('cvFile');
                const textInput = document.getElementById('cvText');
                const btn = document.getElementById('analyzeBtn');
                const errorDiv = document.getElementById('analyzeError');
                const resultSection = document.getElementById('resultSection');
                const skillsContainer = document.getElementById('skillsContainer');
                const redactedBox = document.getElementById('redactedBox');

                const file = fileInput.files[0];
                const texto = textInput.value.trim();

                if (!file && !texto) {
                    errorDiv.textContent = "Por favor, sube un archivo o pega el texto del CV.";
                    errorDiv.classList.remove('hidden');
                    return;
                }

                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> <span>Procesando con IA...</span>';
                errorDiv.classList.add('hidden');
                resultSection.classList.add('hidden');

                try {
                    let response;
                    if (file) {
                        const formData = new FormData();
                        formData.append('file', file);
                        response = await fetch(API_URL + '/cvs/procesar-archivo', {
                            method: 'POST',
                            headers: { 'Authorization': 'Bearer ' + token },
                            body: formData
                        });
                    } else {
                        response = await fetch(API_URL + '/cvs/procesar-ia', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                            body: JSON.stringify({ texto_cv: texto })
                        });
                    }

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Error al procesar");

                    if (data.status === 'pendiente') {
                        skillsContainer.innerHTML = '<p class="text-blue-700 font-semibold text-lg"><i class="fas fa-clock mr-2"></i> ¡Archivo recibido! Se está procesando en segundo plano.</p>';
                        redactedBox.classList.add('hidden');
                    } else {
                        skillsContainer.innerHTML = "";
                        if (data.skills_extraidas && data.skills_extraidas.length > 0) {
                            data.skills_extraidas.forEach(function(skill) {
                                const tag = document.createElement('span');
                                tag.className = 'skill-tag bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-full text-sm font-bold shadow-md';
                                tag.textContent = skill;
                                skillsContainer.appendChild(tag);
                            });
                        }
                        if (data.texto_redactado) {
                            document.getElementById('redactedText').textContent = data.texto_redactado;
                            redactedBox.classList.remove('hidden');
                        }
                    }
                    resultSection.classList.remove('hidden');
                } catch (err) {
                    errorDiv.textContent = "❌ " + err.message;
                    errorDiv.classList.remove('hidden');
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-magic mr-2"></i> <span>Procesar con IA</span>';
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
                
                resultsDiv.innerHTML = '<div class="text-center py-8"><div class="skeleton h-32 w-full rounded-xl mb-4"></div><div class="skeleton h-32 w-full rounded-xl"></div></div>';
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
                        resultsDiv.innerHTML = '<p class="text-center text-gray-500 py-8 text-lg">No se encontraron candidatos con esos requisitos.</p>';
                        return;
                    }

                    data.candidatos.forEach(function(candidato, index) {
                        const card = document.createElement('div');
                        card.className = 'card-enter bg-white p-6 rounded-2xl border-2 border-gray-200 shadow-lg hover:shadow-2xl transition-all duration-300';
                        card.style.animationDelay = (index * 0.1) + 's';
                        
                        const matchColor = candidato.match_porcentaje >= 80 ? 'from-green-500 to-green-600' : 'from-yellow-500 to-yellow-600';
                        
                        let skillsHtml = candidato.skills_coincidentes.map(function(s) { 
                            return '<span class="skill-tag bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md">' + s + '</span>'; 
                        }).join('');
                        
                        let otherSkillsHtml = candidato.todas_las_skills_del_cv.filter(function(s) { 
                            return candidato.skills_coincidentes.map(function(sc) { return sc.toLowerCase(); }).indexOf(s.toLowerCase()) === -1; 
                        }).map(function(s) { 
                            return '<span class="skill-tag bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-xs font-semibold">' + s + '</span>'; 
                        }).join('');

                        const adminButton = esAdmin 
                            ? '<button onclick="revelarIdentidad(\\'' + candidato.perfil_ciego_id + '\\', this)" class="btn-primary bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-5 py-2 rounded-lg transition-all shadow-md"><i class="fas fa-unlock mr-2"></i> Ver Identidad (Admin)</button>'
                            : '<span class="text-xs text-gray-400 font-medium"><i class="fas fa-lock mr-1"></i> Solicita acceso a RR.HH.</span>';

                        card.innerHTML = 
                            '<div class="flex justify-between items-start mb-4 border-b-2 border-gray-100 pb-3">' +
                                '<h4 class="font-bold text-xl text-gray-800">ID: ' + candidato.perfil_ciego_id + '</h4>' +
                                '<span class="match-badge bg-gradient-to-r ' + matchColor + ' text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">' + candidato.match_porcentaje + '% Match</span>' +
                            '</div>' +
                            '<div class="mb-4">' +
                                '<p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-bold">Habilidades que coinciden:</p>' +
                                '<div class="flex flex-wrap gap-2 mb-3">' + (skillsHtml || '<span class="text-gray-400 text-sm">Ninguna</span>') + '</div>' +
                                (otherSkillsHtml ? '<p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-bold mt-3">Otras habilidades:</p><div class="flex flex-wrap gap-2">' + otherSkillsHtml + '</div>' : '') +
                            '</div>' +
                            '<div class="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-xl border-2 border-gray-200">' +
                                '<p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-bold">Perfil Redactado (Anónimo):</p>' +
                                '<p class="text-sm text-gray-700 italic leading-relaxed">' + (candidato.cv_redactado || 'No disponible') + '</p>' +
                            '</div>' +
                            '<div class="mt-5 flex items-center justify-between border-t-2 border-gray-100 pt-4">' +
                                '<span class="text-xs text-gray-500 font-medium"><i class="fas fa-user-shield mr-1"></i> Datos protegidos por privacidad</span>' +
                                adminButton +
                            '</div>' +
                            '<div class="identity-box hidden mt-5 bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-300 p-5 rounded-xl shadow-lg"></div>';
                        
                        resultsDiv.appendChild(card);
                    });
                } catch (err) {
                    resultsDiv.classList.add('hidden');
                    errorDiv.textContent = "❌ " + err.message;
                    errorDiv.classList.remove('hidden');
                }
            }

            async function revelarIdentidad(perfilId, boton) {
                const contenedor = boton.closest('.bg-white').querySelector('.identity-box');
                contenedor.classList.remove('hidden');
                contenedor.innerHTML = '<p class="text-sm text-blue-700 font-semibold"><i class="fas fa-spinner fa-spin mr-2"></i> Verificando permisos...</p>';

                try {
                    const response = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(perfilId) + '/identidad', {
                        method: 'GET',
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Acceso denegado");

                    contenedor.innerHTML = 
                        '<h5 class="text-lg font-bold text-blue-900 mb-3 flex items-center"><i class="fas fa-unlock mr-2"></i> Identidad Revelada (Acción Auditada)</h5>' +
                        '<p class="text-xs text-gray-600 mb-3 font-semibold">Revelado por: <strong class="text-blue-700">' + data.identidad_revelada_por + '</strong></p>' +
                        '<pre class="text-xs text-gray-800 whitespace-pre-wrap bg-white p-4 rounded-lg border-2 border-blue-200 shadow-inner leading-relaxed">' + data.texto_original_completo + '</pre>';
                    
                    boton.disabled = true;
                    boton.innerHTML = '<i class="fas fa-check mr-2"></i> Identidad Revelada';
                    boton.className = 'bg-green-600 text-white text-sm font-bold px-5 py-2 rounded-lg shadow-md cursor-not-allowed';
                } catch (err) {
                    contenedor.innerHTML = '<p class="text-sm text-red-600 font-semibold">🔒 ' + err.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """