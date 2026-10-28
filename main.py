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

app = FastAPI(title="Nexus Inclusivo API", version="2.3.0", lifespan=lifespan)
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
    <title>Nexus Inclusivo</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            min-height: 100vh;
            color: #e2e8f0;
            line-height: 1.6;
        }
        .header {
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
        .flex { display: flex; align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-3 { gap: 12px; }
        .gtext {
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 24px;
        }
        .panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 16px;
            padding: 32px;
            margin-top: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        }
        .inp {
            width: 100%;
            padding: 14px 16px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            color: #f8fafc;
            font-size: 15px;
            outline: none;
            margin-bottom: 16px;
            transition: border-color 0.3s;
        }
        .inp:focus { border-color: #818cf8; }
        .btn {
            padding: 14px 24px;
            border-radius: 10px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            color: white;
            width: 100%;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .grad { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
        .green { background: #059669; }
        .green:hover { background: #047857; }
        .gray { background: #334155; }
        .hidden { display: none !important; }
        .text-sm { font-size: 14px; }
        .text-gray-400 { color: #94a3b8; }
        .text-red-400 { color: #f87171; }
        .text-center { text-align: center; }
        .mb-4 { margin-bottom: 16px; }
        .mb-6 { margin-bottom: 24px; }
        .mt-6 { margin-top: 24px; }
        
        /* Botón flotante de WhatsApp */
        .wa-float {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: #25D366;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 34px;
            box-shadow: 0 8px 25px rgba(37, 211, 102, 0.5);
            z-index: 9999;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        .wa-float:hover { transform: scale(1.1); box-shadow: 0 12px 30px rgba(37, 211, 102, 0.7); }
        
        .card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-top: 20px;
        }
        .chip {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            margin: 4px;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container flex justify-between">
            <div class="flex gap-3">
                <div style="width:45px;height:45px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;display:flex;align-items:center;justify-content:center;">
                    <i class="fas fa-brain text-xl" style="color:white;"></i>
                </div>
                <div>
                    <h1 class="gtext" style="font-size:22px;margin:0;">NEXUS INCLUSIVO</h1>
                    <p class="text-sm text-gray-400" style="margin:0;">AI-Powered Ethical Recruitment</p>
                </div>
            </div>
            <div id="authStatus" class="hidden flex gap-3" style="align-items:center;">
                <i class="fas fa-user-shield" style="color:#4ade80;"></i>
                <span id="userRole" style="font-weight:700;">Admin</span>
                <button onclick="logout()" style="background:none;border:none;color:#94a3b8;cursor:pointer;text-decoration:underline;">Salir</button>
            </div>
        </div>
    </header>

    <main class="container">
        <section id="loginSection" class="panel" style="max-width:450px;margin:60px auto;">
            <h2 class="gtext mb-4" style="text-align:center;">Acceso al Sistema</h2>
            <p class="text-sm text-gray-400 mb-6" style="text-align:center;">Ingresa tus credenciales</p>
            <input id="loginUser" class="inp" placeholder="Usuario">
            <input id="loginPass" class="inp" type="password" placeholder="Contraseña">
            <button id="loginBtn" class="btn grad" onclick="login()">Ingresar al Sistema</button>
            <p id="loginError" class="hidden text-sm text-red-400 mt-6 text-center"></p>
        </section>

        <section id="dashboard" class="hidden">
            <div class="flex gap-3 mb-6" style="margin-bottom:30px;">
                <button id="tab-analyze" class="btn grad" onclick="showTab('analyze')" style="flex:1;">Analizar CV</button>
                <button id="tab-search" class="btn gray" onclick="showTab('search')" style="flex:1;">Buscar Candidatos</button>
            </div>

            <div id="analyzeSection" class="panel">
                <h2 class="gtext mb-6">Procesamiento con IA</h2>
                <label class="text-sm text-gray-400 mb-4" style="display:block;margin-bottom:8px;">Archivo (PDF, DOCX, TXT)</label>
                <input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="inp mb-4" style="padding:10px;">
                
                <label class="text-sm text-gray-400 mb-4" style="display:block;margin-bottom:8px;">
                    <i class="fab fa-whatsapp" style="color:#4ade80;"></i> WhatsApp del candidato (opcional)
                </label>
                <input id="cvWhatsapp" class="inp mb-4" placeholder="+54 9 299 329 3669">
                
                <label class="text-sm text-gray-400 mb-4" style="display:block;margin-bottom:8px;">O pega el texto del CV</label>
                <textarea id="cvText" rows="5" class="inp mb-4"></textarea>
                
                <button id="analyzeBtn" class="btn green" onclick="procesarCV()">Procesar con IA</button>
                <p id="analyzeError" class="hidden text-sm text-red-400 mt-6 text-center"></p>
                <div id="analyzeResult" class="hidden mt-6 text-sm text-center" style="color:#d8b4fe;"></div>
            </div>

            <div id="searchSection" class="panel hidden">
                <h2 class="gtext mb-6">Búsqueda de Candidatos</h2>
                <label class="text-sm text-gray-400 mb-4" style="display:block;margin-bottom:8px;">Habilidades (separadas por coma)</label>
                <input id="searchSkills" class="inp mb-4" placeholder="Python, FastAPI">
                <label class="text-sm text-gray-400 mb-4" style="display:block;margin-bottom:8px;">Match mínimo (%)</label>
                <input id="searchMinMatch" type="number" value="50" class="inp mb-4">
                <button class="btn grad" onclick="buscarCandidatos()">Buscar Candidatos</button>
                <p id="searchError" class="hidden text-sm text-red-400 mt-6 text-center"></p>
                <div id="searchResults" class="mt-6"></div>
            </div>
        </section>
    </main>

    <a class="wa-float" href="https://wa.me/5492993293669?text=Hola,%20quiero%20informacion%20sobre%20Nexus%20Inclusivo" target="_blank" title="Contacto por WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
    
    <footer class="text-center text-sm text-gray-400" style="padding:40px 0;">
        © 2026 Nexus Inclusivo · Powered by AI & Ethical Design
    </footer>

    <script>
        var token = "";
        var API_URL = "https://cv-api-1-ps8r.onrender.com";

        function showTab(name) {
            document.getElementById('analyzeSection').classList.add('hidden');
            document.getElementById('searchSection').classList.add('hidden');
            document.getElementById(name + 'Section').classList.remove('hidden');
            document.getElementById('tab-analyze').className = name === 'analyze' ? 'btn grad' : 'btn gray';
            document.getElementById('tab-search').className = name === 'search' ? 'btn grad' : 'btn gray';
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
            btn.textContent = 'Conectando... (espera 50s)';
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
                btn.textContent = 'Ingresar al Sistema';
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
            btn.textContent = 'Procesando...';
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
                btn.textContent = 'Procesar con IA';
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
            box.innerHTML = '<p class="text-gray-400 mt-6 text-center">Buscando...</p>';
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
                    box.innerHTML = '<p class="text-gray-400 mt-6 text-center">No se encontraron candidatos.</p>';
                    return;
                }
                var admin = getRole() === 'Admin';
                data.candidatos.forEach(function (c) {
                    var card = document.createElement('div');
                    card.className = 'card';
                    var waBtn = c.whatsapp ? '<a class="btn green text-sm" target="_blank" href="https://wa.me/' + c.whatsapp.replace(/[^0-9]/g, '') + '" style="width:auto;padding:10px 16px;"><i class="fab fa-whatsapp"></i> WhatsApp</a>' : '';
                    var revealBtn = admin ? '<button class="btn grad text-sm reveal-btn" style="width:auto;padding:10px 16px;">Revelar Identidad</button>' : '<span class="text-sm text-gray-400">Solo Admin</span>';
                    
                    card.innerHTML =
                        '<div class="flex justify-between mb-4" style="border-bottom:1px solid rgba(148,163,184,0.1);padding-bottom:16px;">' +
                            '<h3 class="gtext" style="font-size:20px;">' + c.perfil_ciego_id + '</h3>' +
                            '<span class="chip" style="background:rgba(74,222,128,0.15);border-color:rgba(74,222,128,0.3);color:#4ade80;">' + c.match_porcentaje + '% MATCH</span>' +
                        '</div>' +
                        '<div class="mb-4">' + (c.skills_coincidentes || []).map(function (s) { return '<span class="chip">' + s + '</span>'; }).join('') + '</div>' +
                        '<p class="text-sm text-gray-400 mb-4" style="background:rgba(0,0,0,0.2);padding:16px;border-radius:10px;font-style:italic;">' + (c.cv_redactado || 'Sin perfil redactado') + '</p>' +
                        '<div class="flex gap-3" style="align-items:center;">' + waBtn + revealBtn + '</div>' +
                        '<div class="identity-box hidden mt-6" style="background:rgba(0,0,0,0.3);padding:16px;border-radius:10px;font-size:13px;"></div>';
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
            var box = btn.closest('.card').querySelector('.identity-box');
            box.classList.remove('hidden');
            box.textContent = 'Verificando permisos...';
            try {
                var res = await fetch(API_URL + '/cvs/perfil/' + encodeURIComponent(id) + '/identidad', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                var data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Acceso denegado');
                
                var html = '<p style="color:#d8b4fe;font-weight:700;margin-bottom:12px;">Identidad revelada por: ' + data.identidad_revelada_por + '</p>';
                if (data.whatsapp) {
                    html += '<p style="color:#4ade80;margin-bottom:12px;font-weight:700;"><i class="fab fa-whatsapp"></i> WhatsApp: ' + data.whatsapp + '</p>';
                }
                html += '<pre style="white-space:pre-wrap;color:#e2e8f0;background:rgba(0,0,0,0.4);padding:16px;border-radius:10px;">' + data.texto_original_completo + '</pre>';
                
                box.innerHTML = html;
                btn.disabled = true;
                btn.textContent = 'Revelado';
                btn.className = 'btn text-sm cursor-not-allowed';
                btn.style.background = '#059669';
                btn.style.width = 'auto';
                btn.style.padding = '10px 16px';
            } catch (e) {
                box.textContent = 'Error: ' + String(e.message);
            }
        }
    </script>
</body>
</html>
"""