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

app = FastAPI(title="Nexus Inclusivo API", version="4.0.0", lifespan=lifespan)
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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Nexus Inclusivo v4.0 - AI Recruitment Platform</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css?v=4.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(240, 147, 251, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        .header {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 2px solid;
            border-image: linear-gradient(90deg, #667eea, #764ba2, #f093fb) 1;
            padding: 24px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            position: relative;
            z-index: 1;
        }
        
        .flex { display: flex; align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-3 { gap: 16px; }
        
        .logo-box {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        
        .logo-box i { color: white; font-size: 28px; }
        
        .brand-title {
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        }
        
        .brand-subtitle {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 2px;
        }
        
        .auth-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(102, 126, 234, 0.1);
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 10px 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .auth-badge i { color: #4ade80; font-size: 20px; }
        .auth-badge span { font-weight: 700; font-size: 15px; }
        
        .logout-btn {
            background: rgba(239, 68, 68, 0.2);
            border: 2px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.3);
            transform: translateY(-2px);
        }
        
        .panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(20px);
            border: 2px solid transparent;
            border-radius: 24px;
            padding: 40px;
            margin-top: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            position: relative;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .panel::before {
            content: '';
            position: absolute;
            top: -2px; left: -2px; right: -2px; bottom: -2px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #667eea);
            border-radius: 24px;
            z-index: -1;
            background-size: 200% 200%;
            animation: gradientShift 8s ease infinite;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .input-field {
            width: 100%;
            padding: 16px 20px;
            background: rgba(15, 23, 42, 0.8);
            border: 2px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            color: #f8fafc;
            font-size: 15px;
            outline: none;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .input-field:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2), 0 0 20px rgba(102, 126, 234, 0.4);
            background: rgba(15, 23, 42, 0.95);
        }
        
        .input-field::placeholder { color: #64748b; }
        
        .button {
            padding: 16px 28px;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            color: white;
            width: 100%;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        
        .button::before {
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            width: 0; height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .button:hover::before { width: 300px; height: 300px; }
        
        .button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5);
        }
        
        .button:active { transform: translateY(-1px); }
        .button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        
        .button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        
        .button-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        }
        
        .button-secondary {
            background: linear-gradient(135deg, #475569 0%, #334155 100%);
        }
        
        .hidden { display: none !important; }
        
        .text-muted { color: #94a3b8; font-size: 14px; }
        .text-error { color: #f87171; font-size: 14px; }
        .text-center { text-align: center; }
        .mb-4 { margin-bottom: 16px; }
        .mb-6 { margin-bottom: 24px; }
        .mt-6 { margin-top: 24px; }
        
        .whatsapp-float {
            position: fixed;
            bottom: 30px; right: 30px;
            width: 70px; height: 70px;
            border-radius: 50%;
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 36px;
            box-shadow: 0 8px 30px rgba(37, 211, 102, 0.6);
            z-index: 9999;
            transition: all 0.3s ease;
            text-decoration: none;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                box-shadow: 0 8px 30px rgba(37, 211, 102, 0.6), 0 0 0 0 rgba(37, 211, 102, 0.7);
            }
            50% {
                box-shadow: 0 8px 30px rgba(37, 211, 102, 0.6), 0 0 0 20px rgba(37, 211, 102, 0);
            }
        }
        
        .whatsapp-float:hover {
            transform: scale(1.15) rotate(8deg);
            box-shadow: 0 12px 40px rgba(37, 211, 102, 0.8);
        }
        
        .candidate-card {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(15px);
            border: 2px solid rgba(148, 163, 184, 0.1);
            border-radius: 20px;
            padding: 32px;
            margin-top: 24px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: fadeInUp 0.5s ease-out;
        }
        
        .candidate-card:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: rgba(102, 126, 234, 0.5);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        }
        
        .skill-chip {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
            border: 2px solid rgba(102, 126, 234, 0.4);
            color: #a5b4fc;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .skill-chip:hover {
            transform: scale(1.1) translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .section-title {
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
        }
        
        .icon-circle {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container flex justify-between">
            <div class="flex gap-3">
                <div class="logo-box">
                    <i class="fas fa-brain"></i>
                </div>
                <div>
                    <h1 class="brand-title">NEXUS INCLUSIVO</h1>
                    <p class="brand-subtitle">AI-Powered Ethical Recruitment Platform v4.0</p>
                </div>
            </div>
            <div id="authStatus" class="hidden">
                <div class="auth-badge">
                    <i class="fas fa-user-shield"></i>
                    <span id="userRole">Admin</span>
                    <button class="logout-btn" onclick="logout()">
                        <i class="fas fa-sign-out-alt"></i> Salir
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main class="container">
        <section id="loginSection" class="panel" style="max-width:500px;margin:80px auto;">
            <div class="text-center mb-6">
                <div class="icon-circle" style="background:linear-gradient(135deg,#667eea,#764ba2);">
                    <i class="fas fa-lock" style="color:white;font-size:32px;"></i>
                </div>
                <h2 class="section-title">Acceso al Sistema</h2>
                <p class="text-muted">Ingresa tus credenciales para continuar</p>
            </div>
            <input id="loginUser" class="input-field" placeholder="Usuario">
            <input id="loginPass" class="input-field" type="password" placeholder="Contraseña">
            <button id="loginBtn" class="button button-primary" onclick="login()">
                <i class="fas fa-sign-in-alt"></i> Ingresar al Sistema
            </button>
            <p id="loginError" class="hidden text-error mt-6 text-center"></p>
        </section>

        <section id="dashboard" class="hidden">
            <div class="flex gap-3 mb-6">
                <button id="tab-analyze" class="button button-primary" onclick="showTab('analyze')" style="flex:1;">
                    <i class="fas fa-file-alt"></i> Analizar CV
                </button>
                <button id="tab-search" class="button button-secondary" onclick="showTab('search')" style="flex:1;">
                    <i class="fas fa-search"></i> Buscar Candidatos
                </button>
            </div>

            <div id="analyzeSection" class="panel">
                <div class="text-center mb-6">
                    <div class="icon-circle" style="background:linear-gradient(135deg,#10b981,#059669);">
                        <i class="fas fa-magic" style="color:white;font-size:28px;"></i>
                    </div>
                    <h2 class="section-title">Procesamiento con IA</h2>
                    <p class="text-muted">Sube un archivo o pega el texto del currículum</p>
                </div>
                
                <label class="text-muted mb-4" style="display:block;font-weight:600;">
                    <i class="fas fa-cloud-upload-alt" style="color:#667eea;"></i> Archivo (PDF, DOCX, TXT)
                </label>
                <input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="input-field" style="padding:12px;">
                
                <label class="text-muted mb-4" style="display:block;font-weight:600;">
                    <i class="fab fa-whatsapp" style="color:#25D366;"></i> WhatsApp del candidato (opcional)
                </label>
                <input id="cvWhatsapp" class="input-field" placeholder="+54 9 299 329 3669">
                
                <label class="text-muted mb-4" style="display:block;font-weight:600;">
                    <i class="fas fa-paste" style="color:#667eea;"></i> O pega el texto del CV
                </label>
                <textarea id="cvText" rows="6" class="input-field" style="resize:none;"></textarea>
                
                <button id="analyzeBtn" class="button button-success" onclick="procesarCV()">
                    <i class="fas fa-magic"></i> Procesar con IA
                </button>
                <p id="analyzeError" class="hidden text-error mt-6 text-center"></p>
                <div id="analyzeResult" class="hidden mt-6 text-center" style="color:#a5b4fc;font-weight:600;"></div>
            </div>

            <div id="searchSection" class="panel hidden">
                <div class="text-center mb-6">
                    <div class="icon-circle" style="background:linear-gradient(135deg,#f093fb,#f5576c);">
                        <i class="fas fa-search" style="color:white;font-size:28px;"></i>
                    </div>
                    <h2 class="section-title">Búsqueda de Candidatos</h2>
                    <p class="text-muted">Encuentra candidatos con Blind Hiring</p>
                </div>
                
                <label class="text-muted mb-4" style="display:block;font-weight:600;">
                    <i class="fas fa-tags" style="color:#667eea;"></i> Habilidades (separadas por coma)
                </label>
                <input id="searchSkills" class="input-field" placeholder="Python, FastAPI, AWS">
                
                <label class="text-muted mb-4" style="display:block;font-weight:600;">
                    <i class="fas fa-percentage" style="color:#667eea;"></i> Match mínimo (%)
                </label>
                <input id="searchMinMatch" type="number" value="50" class="input-field">
                
                <button class="button button-primary" onclick="buscarCandidatos()">
                    <i class="fas fa-search"></i> Buscar Candidatos
                </button>
                <p id="searchError" class="hidden text-error mt-6 text-center"></p>
                <div id="searchResults" class="mt-6"></div>
            </div>
        </section>
    </main>

    <a class="whatsapp-float" href="https://wa.me/5492993293669?text=Hola,%20quiero%20informacion%20sobre%20Nexus%20Inclusivo" target="_blank" title="Contacto por WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
    
    <footer class="text-center text-muted" style="padding:40px 0;position:relative;z-index:1;">
        © 2026 Nexus Inclusivo · Powered by AI & Ethical Design
    </footer>

    <script>
        var token = "";
        var API_URL = "https://cv-api-1-ps8r.onrender.com";

        function showTab(name) {
            document.getElementById('analyzeSection').classList.add('hidden');
            document.getElementById('searchSection').classList.add('hidden');
            document.getElementById(name + 'Section').classList.remove('hidden');
            document.getElementById('tab-analyze').className = name === 'analyze' ? 'button button-primary' : 'button button-secondary';
            document.getElementById('tab-search').className = name === 'search' ? 'button button-primary' : 'button button-secondary';
            document.getElementById('tab-analyze').style.flex = '1';
            document.getElementById('tab-search').style.flex = '1';
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
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Conectando... (espera 50s)';
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
                btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Ingresar al Sistema';
            }
        }

        function logout() {
            token = "";
            document.getElementById('loginSection').classList.remove('hidden');
            document.getElementById('dashboard').classList.add('hidden');
            document.getElementById('authStatus').classList.add('hidden');
        }

        async function procesarCV() {
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
                out.textContent = data.status === 'pendiente' ? 'Archivo recibido. Procesando en segundo plano...' : 'CV procesado: ' + (data.skills_extraidas || []).join(', ');
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
            box.innerHTML = '<p class="text-muted mt-6 text-center" style="font-size:18px;"><i class="fas fa-spinner fa-spin"></i> Buscando candidatos...</p>';
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
                    box.innerHTML = '<p class="text-muted mt-6 text-center" style="font-size:18px;">No se encontraron candidatos.</p>';
                    return;
                }
                var admin = getRole() === 'Admin';
                data.candidatos.forEach(function (c) {
                    var card = document.createElement('div');
                    card.className = 'candidate-card';
                    var waBtn = c.whatsapp ? '<a class="button button-success" target="_blank" href="https://wa.me/' + c.whatsapp.replace(/[^0-9]/g, '') + '" style="width:auto;padding:12px 20px;text-decoration:none;display:inline-flex;align-items:center;gap:8px;"><i class="fab fa-whatsapp" style="font-size:18px;"></i> WhatsApp</a>' : '';
                    var revealBtn = admin ? '<button class="button button-primary reveal-btn" style="width:auto;padding:12px 20px;"><i class="fas fa-unlock"></i> Revelar Identidad</button>' : '<span class="text-muted" style="font-weight:600;"><i class="fas fa-lock"></i> Solo Admin</span>';
                    
                    card.innerHTML =
                        '<div class="flex justify-between mb-4" style="border-bottom:2px solid rgba(148,163,184,0.1);padding-bottom:20px;">' +
                            '<h3 class="section-title" style="font-size:24px;margin:0;">' + c.perfil_ciego_id + '</h3>' +
                            '<span class="skill-chip" style="background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(5,150,105,0.2));border-color:rgba(16,185,129,0.5);color:#4ade80;font-size:14px;font-weight:800;">' + c.match_porcentaje + '% MATCH</span>' +
                        '</div>' +
                        '<div class="mb-4">' +
                            '<p class="text-muted" style="margin-bottom:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;font-size:12px;">Habilidades que coinciden:</p>' +
                            '<div>' + (c.skills_coincidentes || []).map(function (s) { return '<span class="skill-chip">' + s + '</span>'; }).join('') + '</div>' +
                        '</div>' +
                        '<p class="text-muted mb-4" style="background:rgba(0,0,0,0.3);padding:20px;border-radius:12px;font-style:italic;border-left:4px solid #667eea;line-height:1.8;">' + (c.cv_redactado || 'Sin perfil redactado') + '</p>' +
                        '<div class="flex gap-3" style="align-items:center;gap:12px;margin-top:24px;">' + waBtn + revealBtn + '</div>' +
                        '<div class="identity-box hidden mt-6" style="background:rgba(0,0,0,0.4);padding:20px;border-radius:12px;font-size:13px;margin-top:24px;border:2px solid rgba(102,126,234,0.3);"></div>';
                    box.appendChild(card);
                    
                    var rb = card.querySelector('.reveal-btn');
                    if (rb) {
                        rb.addEventListener('click', function () { revelarIdentidad(c.perfil_ciego_id, rb); });
                    }
                });
            } catch (e) {
                err.textContent = String(e.message);
                err.classList.remove('hidden');
            }
        }

        async function revelarIdentidad(id, btn) {
            var box = btn.closest('.candidate-card').querySelector('.identity-box');
            box.classList.remove('hidden');
            box.innerHTML = '<p style="color:#a5b4fc;"><i class="fas fa-spinner fa-spin"></i> Verificando permisos...</p>';
            try {
                var res = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(id) + '/identidad', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Acceso denegado');
                
                var html = '<p style="color:#a5b4fc;font-weight:800;margin-bottom:16px;font-size:16px;"><i class="fas fa-unlock"></i> Identidad revelada por: ' + data.identidad_revelada_por + '</p>';
                if (data.whatsapp) {
                    html += '<p style="color:#4ade80;margin-bottom:16px;font-weight:700;font-size:15px;"><i class="fab fa-whatsapp"></i> WhatsApp: ' + data.whatsapp + '</p>';
                }
                html += '<pre style="white-space:pre-wrap;color:#e2e8f0;background:rgba(0,0,0,0.5);padding:20px;border-radius:12px;line-height:1.8;font-family:monospace;font-size:13px;border:2px solid rgba(102,126,234,0.2);">' + data.texto_original_completo + '</pre>';
                
                box.innerHTML = html;
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-check"></i> Revelado';
                btn.className = 'button';
                btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                btn.style.width = 'auto';
                btn.style.padding = '12px 20px';
            } catch (e) {
                box.innerHTML = '<p style="color:#f87171;font-weight:600;">Error: ' + String(e.message) + '</p>';
            }
        }
    </script>
</body>
</html>
"""