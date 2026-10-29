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

app = FastAPI(title="Nexus Inclusivo API", version="5.0.0", lifespan=lifespan)
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
    <title>Nexus Inclusivo · Plataforma de Reclutamiento Ético</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --border-subtle: #334155;
            --border-muted: #475569;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-subtle: #64748b;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --success: #10b981;
            --success-hover: #059669;
            --warning: #f59e0b;
            --danger: #ef4444;
            --whatsapp: #25D366;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
            font-size: 14px;
            -webkit-font-smoothing: antialiased;
        }
        
        /* Header corporativo */
        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-subtle);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 32px;
        }
        
        .flex { display: flex; align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-3 { gap: 12px; }
        .gap-4 { gap: 16px; }
        
        .logo-mark {
            width: 36px;
            height: 36px;
            background: var(--accent);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo-mark i { color: white; font-size: 18px; }
        
        .brand-name {
            font-size: 17px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }
        
        .brand-tagline {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 400;
        }
        
        .user-chip {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-muted);
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
        }
        
        .user-chip i { color: var(--success); font-size: 14px; }
        .user-chip span { font-weight: 600; color: var(--text-secondary); }
        
        .btn-logout {
            background: transparent;
            border: 1px solid var(--border-muted);
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }
        
        .btn-logout:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border-color: var(--text-muted);
        }
        
        /* Cards y paneles */
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 32px;
            margin-top: 24px;
        }
        
        .card-header {
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .card-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px;
            letter-spacing: -0.3px;
        }
        
        .card-subtitle {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        /* Inputs */
        .field-label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .field-label i { color: var(--text-muted); margin-right: 6px; }
        
        .input {
            width: 100%;
            padding: 10px 14px;
            background: var(--bg-primary);
            border: 1px solid var(--border-muted);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.15s;
            margin-bottom: 16px;
        }
        
        .input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .input::placeholder { color: var(--text-subtle); }
        
        /* Botones */
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            border: none;
            color: white;
            transition: all 0.15s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-family: inherit;
        }
        
        .btn:hover { transform: translateY(-1px); }
        .btn:active { transform: translateY(0); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .btn-primary {
            background: var(--accent);
            width: 100%;
        }
        
        .btn-primary:hover { background: var(--accent-hover); }
        
        .btn-success {
            background: var(--success);
            width: 100%;
        }
        
        .btn-success:hover { background: var(--success-hover); }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            width: 100%;
            border: 1px solid var(--border-muted);
        }
        
        .btn-secondary:hover {
            background: var(--border-muted);
            color: var(--text-primary);
        }
        
        .btn-sm {
            padding: 8px 14px;
            font-size: 13px;
            width: auto;
        }
        
        .btn-whatsapp {
            background: var(--whatsapp);
        }
        
        .btn-whatsapp:hover { background: #1fb855; }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 4px;
            background: var(--bg-secondary);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
            margin-bottom: 24px;
        }
        
        .tab {
            flex: 1;
            padding: 10px 16px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.15s;
            font-family: inherit;
        }
        
        .tab:hover { color: var(--text-secondary); }
        
        .tab.active {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-weight: 600;
        }
        
        /* Utilities */
        .hidden { display: none !important; }
        .text-center { text-align: center; }
        .text-muted { color: var(--text-muted); }
        .text-error { color: var(--danger); font-size: 13px; }
        .mb-4 { margin-bottom: 16px; }
        .mb-6 { margin-bottom: 24px; }
        .mt-6 { margin-top: 24px; }
        
        /* Login */
        .login-card {
            max-width: 400px;
            margin: 80px auto;
        }
        
        .login-icon {
            width: 56px;
            height: 56px;
            background: var(--accent);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        
        .login-icon i { color: white; font-size: 24px; }
        
        /* Candidate cards */
        .candidate {
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 24px;
            margin-top: 16px;
            transition: border-color 0.15s;
        }
        
        .candidate:hover { border-color: var(--border-muted); }
        
        .candidate-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 16px;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .candidate-id {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            font-family: 'SF Mono', Monaco, monospace;
        }
        
        .match-badge {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--success);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 700;
        }
        
        .skill-tag {
            display: inline-block;
            padding: 4px 10px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-muted);
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
            margin: 3px 3px 3px 0;
        }
        
        .skill-tag.match {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
            color: #60a5fa;
        }
        
        .redacted-text {
            background: var(--bg-primary);
            border: 1px solid var(--border-subtle);
            padding: 16px;
            border-radius: 6px;
            font-size: 13px;
            color: var(--text-secondary);
            font-style: italic;
            line-height: 1.7;
            margin: 16px 0;
        }
        
        .section-label {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-subtle);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }
        
        .candidate-actions {
            display: flex;
            gap: 8px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-subtle);
            align-items: center;
            justify-content: space-between;
        }
        
        .privacy-note {
            font-size: 12px;
            color: var(--text-subtle);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .identity-box {
            margin-top: 16px;
            padding: 16px;
            background: var(--bg-primary);
            border: 1px solid var(--accent);
            border-radius: 6px;
            font-size: 13px;
        }
        
        .identity-box pre {
            white-space: pre-wrap;
            color: var(--text-secondary);
            background: var(--bg-secondary);
            padding: 12px;
            border-radius: 4px;
            margin-top: 12px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 12px;
            line-height: 1.6;
        }
        
        /* WhatsApp flotante discreto */
        .wa-float {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: var(--whatsapp);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 999;
            text-decoration: none;
            transition: all 0.2s;
        }
        
        .wa-float:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(37, 211, 102, 0.4);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 32px 0;
            color: var(--text-subtle);
            font-size: 12px;
            border-top: 1px solid var(--border-subtle);
            margin-top: 48px;
        }
        
        /* Divider */
        .divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 24px 0;
            color: var(--text-subtle);
            font-size: 12px;
            font-weight: 500;
        }
        
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--border-subtle);
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container flex justify-between">
            <div class="flex gap-3">
                <div class="logo-mark">
                    <i class="fas fa-brain"></i>
                </div>
                <div>
                    <div class="brand-name">Nexus Inclusivo</div>
                    <div class="brand-tagline">Plataforma de Reclutamiento Ético</div>
                </div>
            </div>
            <div id="authStatus" class="hidden flex gap-3">
                <div class="user-chip">
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
        <section id="loginSection" class="card login-card">
            <div class="text-center mb-6">
                <div class="login-icon">
                    <i class="fas fa-lock"></i>
                </div>
                <h1 class="card-title text-center">Iniciar sesión</h1>
                <p class="card-subtitle text-center">Accede a tu cuenta para continuar</p>
            </div>
            <label class="field-label">Usuario</label>
            <input id="loginUser" class="input" placeholder="tu.usuario">
            <label class="field-label">Contraseña</label>
            <input id="loginPass" class="input" type="password" placeholder="••••••••">
            <button id="loginBtn" class="btn btn-primary" onclick="login()" style="margin-top:8px;">
                Ingresar al sistema
            </button>
            <p id="loginError" class="hidden text-error mt-6 text-center"></p>
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
                <div class="card-header">
                    <h2 class="card-title">Procesamiento de currículum</h2>
                    <p class="card-subtitle">Analiza un CV con inteligencia artificial de forma ética y privada</p>
                </div>
                
                <label class="field-label">
                    <i class="fas fa-file-upload"></i> Archivo (PDF, DOCX, TXT)
                </label>
                <input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="input">
                
                <label class="field-label">
                    <i class="fab fa-whatsapp"></i> WhatsApp del candidato (opcional)
                </label>
                <input id="cvWhatsapp" class="input" placeholder="+54 9 299 329 3669">
                <p class="text-muted" style="font-size:12px;margin-top:-10px;margin-bottom:16px;">
                    Solo visible para administradores al revelar identidad
                </p>
                
                <div class="divider">o</div>
                
                <label class="field-label">
                    <i class="fas fa-paste"></i> Texto del currículum
                </label>
                <textarea id="cvText" rows="6" class="input" style="resize:vertical;min-height:120px;" placeholder="Pega aquí el contenido del CV..."></textarea>
                
                <button id="analyzeBtn" class="btn btn-success" onclick="procesarCV()" style="margin-top:8px;">
                    <i class="fas fa-magic"></i> Procesar con IA
                </button>
                <p id="analyzeError" class="hidden text-error mt-6 text-center"></p>
                <div id="analyzeResult" class="hidden mt-6 text-center" style="color:var(--text-secondary);"></div>
            </div>

            <div id="searchSection" class="card hidden">
                <div class="card-header">
                    <h2 class="card-title">Búsqueda de candidatos</h2>
                    <p class="card-subtitle">Encuentra profesionales con el método Blind Hiring</p>
                </div>
                
                <label class="field-label">
                    <i class="fas fa-tags"></i> Habilidades requeridas
                </label>
                <input id="searchSkills" class="input" placeholder="Python, FastAPI, AWS">
                
                <label class="field-label">
                    <i class="fas fa-percent"></i> Coincidencia mínima (%)
                </label>
                <input id="searchMinMatch" type="number" value="50" class="input">
                
                <button class="btn btn-primary" onclick="buscarCandidatos()" style="margin-top:8px;">
                    <i class="fas fa-search"></i> Buscar candidatos
                </button>
                <p id="searchError" class="hidden text-error mt-6 text-center"></p>
                <div id="searchResults" class="mt-6"></div>
            </div>
        </section>
    </main>

    <a class="wa-float" href="https://wa.me/5492993293669?text=Hola,%20quiero%20informacion%20sobre%20Nexus%20Inclusivo" target="_blank" title="Contacto institucional">
        <i class="fab fa-whatsapp"></i>
    </a>
    
    <footer class="footer">
        © 2026 Nexus Inclusivo · Reclutamiento ético potenciado por IA
    </footer>

    <script>
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
                out.textContent = data.status === 'pendiente' ? 'Archivo recibido. Procesando en segundo plano...' : 'CV procesado correctamente.';
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
                    box.innerHTML = '<p class="text-muted mt-6 text-center">No se encontraron candidatos con esos criterios.</p>';
                    return;
                }
                var admin = getRole() === 'Admin';
                data.candidatos.forEach(function (c) {
                    var card = document.createElement('div');
                    card.className = 'candidate';
                    
                    var skillsHtml = (c.skills_coincidentes || []).map(function (s) {
                        return '<span class="skill-tag match">' + s + '</span>';
                    }).join('');
                    
                    var otherSkills = (c.todas_las_skills_del_cv || []).filter(function (s) {
                        return (c.skills_coincidentes || []).map(function (sc) { return sc.toLowerCase(); }).indexOf(s.toLowerCase()) === -1;
                    });
                    var otherHtml = otherSkills.map(function (s) {
                        return '<span class="skill-tag">' + s + '</span>';
                    }).join('');
                    
                    var waBtn = c.whatsapp ? '<a class="btn btn-sm btn-whatsapp" target="_blank" href="https://wa.me/' + c.whatsapp.replace(/[^0-9]/g, '') + '" title="Contactar por WhatsApp"><i class="fab fa-whatsapp"></i> WhatsApp</a>' : '';
                    var revealBtn = admin ? '<button class="btn btn-sm btn-primary reveal-btn"><i class="fas fa-unlock"></i> Revelar identidad</button>' : '';
                    
                    card.innerHTML =
                        '<div class="candidate-header">' +
                            '<div>' +
                                '<div class="section-label">Perfil ciego</div>' +
                                '<div class="candidate-id">' + c.perfil_ciego_id + '</div>' +
                            '</div>' +
                            '<span class="match-badge">' + c.match_porcentaje + '% match</span>' +
                        '</div>' +
                        '<div class="section-label">Habilidades coincidentes</div>' +
                        '<div style="margin-bottom:16px;">' + (skillsHtml || '<span class="text-muted">Ninguna</span>') + '</div>' +
                        (otherHtml ? '<div class="section-label">Otras habilidades</div><div style="margin-bottom:16px;">' + otherHtml + '</div>' : '') +
                        '<div class="section-label">Perfil redactado (anónimo)</div>' +
                        '<div class="redacted-text">' + (c.cv_redactado || 'Sin perfil redactado') + '</div>' +
                        '<div class="candidate-actions">' +
                            '<span class="privacy-note"><i class="fas fa-shield-alt"></i> Datos protegidos por privacidad</span>' +
                            '<div style="display:flex;gap:8px;">' + waBtn + revealBtn + '</div>' +
                        '</div>' +
                        '<div class="identity-box hidden"></div>';
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
            box.innerHTML = '<p style="color:var(--text-secondary);"><i class="fas fa-spinner fa-spin"></i> Verificando permisos...</p>';
            try {
                var res = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(id) + '/identidad', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Acceso denegado');
                
                var html = '<div style="margin-bottom:12px;"><span class="section-label">Revelado por</span><div style="color:var(--text-primary);font-weight:600;">' + data.identidad_revelada_por + '</div></div>';
                
                if (data.whatsapp) {
                    html += '<div style="margin-bottom:12px;"><span class="section-label">Contacto directo</span><div style="color:var(--success);font-weight:600;"><i class="fab fa-whatsapp"></i> ' + data.whatsapp + '</div></div>';
                }
                
                html += '<div class="section-label">Texto original completo</div>';
                html += '<pre>' + data.texto_original_completo + '</pre>';
                
                box.innerHTML = html;
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-check"></i> Revelado';
                btn.style.background = 'var(--bg-tertiary)';
                btn.style.color = 'var(--text-muted)';
                btn.style.cursor = 'not-allowed';
            } catch (e) {
                box.innerHTML = '<p style="color:var(--danger);">Error: ' + String(e.message) + '</p>';
            }
        }
    </script>
</body>
</html>
"""