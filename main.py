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
            .gradient-bg { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
            .glass-panel { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
            .skill-tag { transition: all 0.3s ease; }
            .skill-tag:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .tab-active { border-bottom: 3px solid #2563eb; color: #2563eb; font-weight: 600; }
            .tab-inactive { border-bottom: 3px solid transparent; color: #6b7280; }
            .tab-inactive:hover { color: #374151; }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen font-sans text-gray-800">
        <header class="gradient-bg text-white p-6 shadow-lg">
            <div class="max-w-5xl mx-auto flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-brain text-3xl"></i>
                    <div>
                        <h1 class="text-2xl font-bold">Nexus Inclusivo</h1>
                        <p class="text-blue-100 text-sm">Reclutamiento Inteligente y Ético con IA</p>
                    </div>
                </div>
                <div id="authStatus" class="hidden items-center space-x-2 bg-blue-800 px-3 py-1 rounded-full text-sm">
                    <i class="fas fa-user-shield text-green-400"></i>
                    <span id="userRole">Sesión Activa</span>
                    <button onclick="logout()" class="ml-3 text-blue-200 hover:text-white underline text-xs">Salir</button>
                </div>
            </div>
        </header>

        <main class="max-w-5xl mx-auto p-6 space-y-6">
            <div id="loginSection" class="glass-panel p-6 rounded-xl shadow-md border border-gray-200 max-w-md mx-auto mt-10">
                <h2 class="text-xl font-semibold mb-4 flex items-center"><i class="fas fa-lock mr-2 text-blue-600"></i> Iniciar Sesión</h2>
                <div class="space-y-4">
                    <input type="text" id="loginUser" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Usuario (Ej: Admin)">
                    <input type="password" id="loginPass" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Contraseña">
                    <button id="loginBtn" onclick="login()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition">
                        <i class="fas fa-sign-in-alt mr-2"></i> Ingresar al Sistema
                    </button>
                    <p id="loginError" class="text-red-500 text-sm mt-2 hidden text-center"></p>
                </div>
            </div>

            <div id="mainDashboard" class="hidden">
                <div class="flex border-b border-gray-200 mb-6">
                    <button id="tab-analyze" onclick="showTab('analyze')" class="tab-active px-6 py-3 text-lg flex items-center space-x-2 transition">
                        <i class="fas fa-file-alt"></i> <span>Analizar Nuevo CV</span>
                    </button>
                    <button id="tab-search" onclick="showTab('search')" class="tab-inactive px-6 py-3 text-lg flex items-center space-x-2 transition">
                        <i class="fas fa-search"></i> <span>Buscar Candidatos</span>
                    </button>
                </div>

                <div id="analyzeSection" class="glass-panel p-6 rounded-xl shadow-md border border-gray-200">
                    <h2 class="text-xl font-semibold mb-4">Procesar Currículum con IA</h2>
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Opción A: Subir archivo (PDF, DOCX, TXT)</label>
                            <input type="file" id="cvFile" accept=".pdf,.docx,.txt" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                        </div>
                        <div class="relative flex py-2 items-center">
                            <div class="flex-grow border-t border-gray-300"></div>
                            <span class="flex-shrink-0 mx-4 text-gray-400 text-sm font-medium">O pega el texto</span>
                            <div class="flex-grow border-t border-gray-300"></div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Opción B: Pegar texto del CV</label>
                            <textarea id="cvText" rows="6" class="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm" placeholder="Ej: Ingeniero de Software con 4 años de experiencia..."></textarea>
                        </div>
                    </div>
                    <button id="analyzeBtn" onclick="procesarCV()" class="mt-4 w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2">
                        <i class="fas fa-magic"></i> <span>Procesar con IA</span>
                    </button>
                    <div id="resultSection" class="hidden mt-6 space-y-4">
                        <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                            <h3 class="font-semibold text-blue-800 mb-2">🎯 Resultado:</h3>
                            <div id="skillsContainer" class="flex flex-wrap gap-2"></div>
                        </div>
                        <div id="redactedBox" class="hidden bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <h3 class="font-semibold text-gray-700 mb-2">🔒 Texto Redactado:</h3>
                            <p id="redactedText" class="text-sm text-gray-600 italic"></p>
                        </div>
                    </div>
                    <p id="analyzeError" class="text-red-500 text-sm mt-2 hidden text-center"></p>
                </div>

                <div id="searchSection" class="hidden glass-panel p-6 rounded-xl shadow-md border border-gray-200">
                    <h2 class="text-xl font-semibold mb-4">Búsqueda de Candidatos (Blind Hiring)</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Habilidades requeridas (separadas por coma)</label>
                            <input type="text" id="searchSkills" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none" placeholder="Ej: Python, AWS, Docker">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Coincidencia mínima (%)</label>
                            <input type="number" id="searchMinMatch" value="50" min="0" max="100" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none">
                        </div>
                    </div>
                    <button onclick="buscarCandidatos()" class="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2">
                        <i class="fas fa-search"></i> <span>Buscar Candidatos</span>
                    </button>
                    <div id="searchResults" class="hidden mt-6 space-y-4"></div>
                    <p id="searchError" class="text-red-500 text-sm mt-2 hidden text-center"></p>
                </div>
            </div>
        </main>
        <footer class="text-center p-6 text-gray-500 text-sm">&copy; 2026 Nexus Inclusivo Core.</footer>

        <script>
            let token = "";
            const API_URL = "https://cv-api-1-ps8r.onrender.com";

            function showTab(tabName) {
                document.getElementById('analyzeSection').classList.add('hidden');
                document.getElementById('searchSection').classList.add('hidden');
                document.getElementById('tab-analyze').className = "tab-inactive px-6 py-3 text-lg flex items-center space-x-2 transition";
                document.getElementById('tab-search').className = "tab-inactive px-6 py-3 text-lg flex items-center space-x-2 transition";
                document.getElementById(tabName + 'Section').classList.remove('hidden');
                document.getElementById('tab-' + tabName).className = "tab-active px-6 py-3 text-lg flex items-center space-x-2 transition";
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
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Procesando...</span>';
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
                        skillsContainer.innerHTML = '<p class="text-blue-600 font-semibold"><i class="fas fa-clock"></i> ¡Archivo recibido! Se está procesando en segundo plano.</p>';
                        redactedBox.classList.add('hidden');
                    } else {
                        skillsContainer.innerHTML = "";
                        if (data.skills_extraidas && data.skills_extraidas.length > 0) {
                            data.skills_extraidas.forEach(function(skill) {
                                const tag = document.createElement('span');
                                tag.className = 'skill-tag bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold border border-blue-200';
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
                    btn.innerHTML = '<i class="fas fa-magic"></i> <span>Procesar con IA</span>';
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
                
                resultsDiv.innerHTML = '<p class="text-center text-gray-500 py-4"><i class="fas fa-spinner fa-spin"></i> Buscando...</p>';
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
                        resultsDiv.innerHTML = '<p class="text-center text-gray-500 py-4">No se encontraron candidatos con esos requisitos.</p>';
                        return;
                    }

                    data.candidatos.forEach(function(candidato) {
                        const card = document.createElement('div');
                        card.className = 'bg-white p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition';
                        const matchColor = candidato.match_porcentaje >= 80 ? 'text-green-700 bg-green-100 border-green-200' : 'text-yellow-700 bg-yellow-100 border-yellow-200';
                        
                        let skillsHtml = candidato.skills_coincidentes.map(function(s) { 
                            return '<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-semibold mr-1 mb-1 inline-block">' + s + '</span>'; 
                        }).join('');
                        
                        let otherSkillsHtml = candidato.todas_las_skills_del_cv.filter(function(s) { 
                            return candidato.skills_coincidentes.map(function(sc) { return sc.toLowerCase(); }).indexOf(s.toLowerCase()) === -1; 
                        }).map(function(s) { 
                            return '<span class="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs mr-1 mb-1 inline-block">' + s + '</span>'; 
                        }).join('');

                        const adminButton = esAdmin 
                            ? '<button onclick="revelarIdentidad(\\'' + candidato.perfil_ciego_id + '\\', this)" class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition"><i class="fas fa-unlock mr-1"></i> Ver Identidad (Admin)</button>'
                            : '<span class="text-xs text-gray-400"><i class="fas fa-lock"></i> Solicita acceso a RR.HH.</span>';

                        card.innerHTML = 
                            '<div class="flex justify-between items-start mb-3 border-b border-gray-100 pb-2">' +
                                '<h4 class="font-bold text-lg text-gray-800">ID: ' + candidato.perfil_ciego_id + '</h4>' +
                                '<span class="' + matchColor + ' px-3 py-1 rounded-full text-sm font-bold border">' + candidato.match_porcentaje + '% Match</span>' +
                            '</div>' +
                            '<div class="mb-3">' +
                                '<p class="text-xs text-gray-500 mb-1 uppercase tracking-wide font-semibold">Habilidades que coinciden:</p>' +
                                '<div class="flex flex-wrap mb-2">' + (skillsHtml || '<span class="text-gray-400 text-sm">Ninguna</span>') + '</div>' +
                                (otherSkillsHtml ? '<p class="text-xs text-gray-500 mb-1 uppercase tracking-wide font-semibold mt-2">Otras habilidades:</p><div class="flex flex-wrap">' + otherSkillsHtml + '</div>' : '') +
                            '</div>' +
                            '<div class="bg-gray-50 p-3 rounded border border-gray-200">' +
                                '<p class="text-xs text-gray-500 mb-1 uppercase tracking-wide font-semibold">Perfil Redactado (Anónimo):</p>' +
                                '<p class="text-sm text-gray-700 italic leading-relaxed">' + (candidato.cv_redactado || 'No disponible') + '</p>' +
                            '</div>' +
                            '<div class="mt-4 flex items-center justify-between border-t border-gray-100 pt-3">' +
                                '<span class="text-xs text-gray-500"><i class="fas fa-user-shield"></i> Datos protegidos por privacidad</span>' +
                                adminButton +
                            '</div>' +
                            '<div class="identity-box hidden mt-4 bg-blue-50 border border-blue-200 p-4 rounded-lg"></div>';
                        
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
                contenedor.innerHTML = '<p class="text-sm text-blue-600"><i class="fas fa-spinner fa-spin"></i> Verificando permisos...</p>';

                try {
                    const response = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(perfilId) + '/identidad', {
                        method: 'GET',
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Acceso denegado");

                    contenedor.innerHTML = 
                        '<h5 class="text-sm font-bold text-blue-800 mb-2"><i class="fas fa-unlock"></i> Identidad Revelada (Acción Auditada)</h5>' +
                        '<p class="text-xs text-gray-500 mb-2">Revelado por: <strong>' + data.identidad_revelada_por + '</strong></p>' +
                        '<pre class="text-xs text-gray-700 whitespace-pre-wrap bg-white p-3 rounded border border-blue-100">' + data.texto_original_completo + '</pre>';
                    
                    boton.disabled = true;
                    boton.innerHTML = '<i class="fas fa-check"></i> Identidad Revelada';
                } catch (err) {
                    contenedor.innerHTML = '<p class="text-sm text-red-600">🔒 ' + err.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """
