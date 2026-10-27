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

app = FastAPI(
    title="Mi API MVP", 
    version="0.1.0", 
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/health")
def health():
    return {"status": "ok"}

# 🔥 SOLUCIÓN INFALIBLE: El HTML vive directamente en main.py
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nexus Inclusivo | Analizador de CVs con IA</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
            .glass-panel { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
            .skill-tag { transition: all 0.3s ease; }
            .skill-tag:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen font-sans text-gray-800">
        <header class="gradient-bg text-white p-6 shadow-lg">
            <div class="max-w-4xl mx-auto flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-brain text-3xl"></i>
                    <div>
                        <h1 class="text-2xl font-bold">Nexus Inclusivo</h1>
                        <p class="text-blue-100 text-sm">Analizador de Currículums con Inteligencia Artificial</p>
                    </div>
                </div>
                <div id="authStatus" class="hidden flex items-center space-x-2 bg-blue-800 px-3 py-1 rounded-full text-sm">
                    <i class="fas fa-check-circle text-green-400"></i>
                    <span>Sesión Activa</span>
                </div>
            </div>
        </header>

        <main class="max-w-4xl mx-auto p-6 space-y-6">
            <div id="loginSection" class="glass-panel p-6 rounded-xl shadow-md border border-gray-200">
                <h2 class="text-xl font-semibold mb-4 flex items-center"><i class="fas fa-lock mr-2 text-blue-600"></i> 1. Iniciar Sesión</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
                        <input type="text" id="loginUser" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ej: Admin">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                        <input type="password" id="loginPass" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="••••••••">
                    </div>
                </div>
                <button onclick="login()" class="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2">
                    <i class="fas fa-sign-in-alt"></i> <span>Ingresar al Sistema</span>
                </button>
                <p id="loginError" class="text-red-500 text-sm mt-2 hidden"></p>
            </div>

            <div id="analysisSection" class="hidden glass-panel p-6 rounded-xl shadow-md border border-gray-200">
                <h2 class="text-xl font-semibold mb-4 flex items-center"><i class="fas fa-file-alt mr-2 text-blue-600"></i> 2. Analizar Currículum</h2>
                <label class="block text-sm font-medium text-gray-700 mb-2">Pega el texto del CV aquí:</label>
                <textarea id="cvText" rows="6" class="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm" placeholder="Ej: Ingeniero de Software con 4 años de experiencia en Python, FastAPI, Docker y AWS..."></textarea>
                <button id="analyzeBtn" onclick="procesarCV()" class="mt-4 w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2">
                    <i class="fas fa-magic"></i> <span>Procesar con IA</span>
                </button>

                <div id="resultSection" class="hidden mt-6 space-y-4">
                    <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h3 class="font-semibold text-blue-800 mb-2">🎯 Habilidades Detectadas:</h3>
                        <div id="skillsContainer" class="flex flex-wrap gap-2"></div>
                    </div>
                    <div id="redactedBox" class="hidden bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <h3 class="font-semibold text-gray-700 mb-2">🔒 Texto con datos sensibles redactados:</h3>
                        <p id="redactedText" class="text-sm text-gray-600 italic"></p>
                    </div>
                </div>
                <p id="analyzeError" class="text-red-500 text-sm mt-2 hidden text-center"></p>
            </div>
        </main>

        <footer class="text-center p-6 text-gray-500 text-sm">
            &copy; 2026 Nexus Inclusivo Core. Potenciado por FastAPI & OpenAI.
        </footer>

        <script>
            let token = "";
            const API_URL = "https://cv-api-1-ps8r.onrender.com";

            async function login() {
                const user = document.getElementById('loginUser').value;
                const pass = document.getElementById('loginPass').value;
                const errorDiv = document.getElementById('loginError');

                if (!user || !pass) {
                    errorDiv.textContent = "Por favor completa todos los campos.";
                    errorDiv.classList.remove('hidden');
                    return;
                }

                const formData = new URLSearchParams();
                formData.append('username', user);
                formData.append('password', pass);

                try {
                    const response = await fetch(`${API_URL}/usuarios/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: formData
                    });

                    if (!response.ok) throw new Error("Usuario o contraseña incorrectos");
                    const data = await response.json();
                    token = data.access_token;
                    
                    document.getElementById('loginSection').classList.add('hidden');
                    document.getElementById('analysisSection').classList.remove('hidden');
                    document.getElementById('authStatus').classList.remove('hidden');
                    errorDiv.classList.add('hidden');
                } catch (err) {
                    errorDiv.textContent = "❌ " + err.message;
                    errorDiv.classList.remove('hidden');
                }
            }

            async function procesarCV() {
                const cvText = document.getElementById('cvText').value;
                const btn = document.getElementById('analyzeBtn');
                const errorDiv = document.getElementById('analyzeError');
                const resultSection = document.getElementById('resultSection');
                const skillsContainer = document.getElementById('skillsContainer');
                const redactedBox = document.getElementById('redactedBox');

                if (!cvText) {
                    errorDiv.textContent = "Por favor ingresa el texto del CV.";
                    errorDiv.classList.remove('hidden');
                    return;
                }

                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Analizando con IA...</span>';
                errorDiv.classList.add('hidden');
                resultSection.classList.add('hidden');

                try {
                    const response = await fetch(`${API_URL}/cvs/procesar-ia`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                        body: JSON.stringify({ texto_cv: cvText })
                    });

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || "Error al procesar el CV");

                    skillsContainer.innerHTML = "";
                    if (data.skills_extraidas && data.skills_extraidas.length > 0) {
                        data.skills_extraidas.forEach(skill => {
                            const tag = document.createElement('span');
                            tag.className = 'skill-tag bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold border border-blue-200';
                            tag.textContent = skill;
                            skillsContainer.appendChild(tag);
                        });
                    } else {
                        skillsContainer.innerHTML = '<p class="text-gray-500">No se detectaron habilidades claras.</p>';
                    }

                    if (data.texto_redactado) {
                        document.getElementById('redactedText').textContent = data.texto_redactado;
                        redactedBox.classList.remove('hidden');
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
        </script>
    </body>
    </html>
    """
