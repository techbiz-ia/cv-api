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

app = FastAPI(title="Nexus Inclusivo API", version="2.2.0", lifespan=lifespan)
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
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
body{background:linear-gradient(135deg,#0a0a0a,#1a1a2e,#16213e);min-height:100vh;color:#e0e0e0;font-family:system-ui,sans-serif}
.panel{background:rgba(255,255,255,.05);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:32px}
.grad{background:linear-gradient(135deg,#667eea,#764ba2)}
.gtext{background:linear-gradient(135deg,#8b9cf5,#c58bf0);-webkit-background-clip:text;color:transparent}
.inp{width:100%;padding:14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.15);border-radius:12px;color:#fff;outline:none}
.inp:focus{border-color:#667eea}
.btn{padding:14px 20px;border-radius:12px;font-weight:700;cursor:pointer;transition:.25s;border:none;color:#fff}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(102,126,234,.35)}
.btn:disabled{opacity:.6;cursor:wait;transform:none}
.chip{padding:5px 12px;border-radius:999px;font-size:12px;font-weight:600;background:rgba(102,126,234,.2);border:1px solid rgba(102,126,234,.35);margin:3px;display:inline-block}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:26px;margin-top:20px;transition:.3s}
.card:hover{transform:translateY(-5px);box-shadow:0 15px 40px rgba(102,126,234,.25)}
.hidden{display:none!important}
.wa{position:fixed;bottom:28px;right:28px;width:62px;height:62px;border-radius:50%;background:#25d366;display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px;box-shadow:0 8px 30px rgba(37,211,102,.45);z-index:99;transition:.25s;text-decoration:none}
.wa:hover{transform:scale(1.1)}
</style>
</head>
<body>
<header class="p-6 border-b border-gray-800">
  <div class="max-w-5xl mx-auto flex justify-between items-center">
    <div class="flex items-center gap-3">
      <div class="grad w-11 h-11 rounded-xl flex items-center justify-center"><i class="fas fa-brain text-xl text-white"></i></div>
      <div><h1 class="text-xl font-black gtext">NEXUS INCLUSIVO</h1><p class="text-xs text-gray-400">AI-Powered Ethical Recruitment</p></div>
    </div>
    <div id="authStatus" class="hidden text-sm flex items-center gap-2">
      <i class="fas fa-user-shield text-green-400"></i>
      <span id="userRole">Admin</span>
      <button onclick="logout()" class="ml-4 text-gray-400 hover:text-white underline">Salir</button>
    </div>
  </div>
</header>

<main class="max-w-5xl mx-auto p-6">
  <section id="loginSection" class="panel max-w-md mx-auto mt-16">
    <h2 class="text-2xl font-black gtext mb-2">Acceso al Sistema</h2>
    <p class="text-sm text-gray-400 mb-6">Ingresa tus credenciales</p>
    <input id="loginUser" class="inp mb-4" placeholder="Usuario">
    <input id="loginPass" class="inp mb-4" type="password" placeholder="Contraseña">
    <button id="loginBtn" class="btn grad w-full" onclick="login()">Ingresar al Sistema</button>
    <p id="loginError" class="hidden text-red-400 text-sm mt-4 text-center"></p>
  </section>

  <section id="dashboard" class="hidden">
    <div class="flex gap-3 mb-6">
      <button id="tab-analyze" class="btn grad flex-1" onclick="showTab('analyze')">Analizar CV</button>
      <button id="tab-search" class="btn bg-gray-700 flex-1" onclick="showTab('search')">Buscar Candidatos</button>
    </div>

    <div id="analyzeSection" class="panel">
      <h2 class="text-2xl font-black gtext mb-6">Procesamiento con IA</h2>
      <label class="block text-sm text-gray-300 mb-2">Archivo (PDF, DOCX, TXT)</label>
      <input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="inp mb-5 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-600 file:text-white hover:file:bg-purple-700">
      <label class="block text-sm text-gray-300 mb-2"><i class="fab fa-whatsapp text-green-400"></i> WhatsApp del candidato (opcional)</label>
      <input id="cvWhatsapp" class="inp mb-5" placeholder="+54 9 299 329 3669">
      <label class="block text-sm text-gray-300 mb-2">O pega el texto del CV</label>
      <textarea id="cvText" rows="5" class="inp mb-5"></textarea>
      <button id="analyzeBtn" class="btn bg-green-600 w-full" onclick="procesarCV()">Procesar con IA</button>
      <p id="analyzeError" class="hidden text-red-400 text-sm mt-4 text-center"></p>
      <div id="analyzeResult" class="hidden mt-6 text-sm text-purple-300 text-center"></div>
    </div>

    <div id="searchSection" class="panel hidden">
      <h2 class="text-2xl font-black gtext mb-6">Búsqueda de Candidatos</h2>
      <label class="block text-sm text-gray-300 mb-2">Habilidades (separadas por coma)</label>
      <input id="searchSkills" class="inp mb-4" placeholder="Python, FastAPI">
      <label class="block text-sm text-gray-300 mb-2">Match mínimo (%)</label>
      <input id="searchMinMatch" type="number" value="50" class="inp mb-5">
      <button class="btn grad w-full" onclick="buscarCandidatos()">Buscar Candidatos</button>
      <p id="searchError" class="hidden text-red-400 text-sm mt-4 text-center"></p>
      <div id="searchResults" class="mt-6"></div>
    </div>
  </section>
</main>

<a class="wa" href="https://wa.me/5492993293669?text=Hola,%20quiero%20informacion%20sobre%20Nexus%20Inclusivo" target="_blank" title="Contacto por WhatsApp"><i class="fab fa-whatsapp"></i></a>
<footer class="text-center text-xs text-gray-500 py-8">© 2026 Nexus Inclusivo · Powered by AI & Ethical Design</footer>

<script>
var token = "";
var API_URL = "https://cv-api-1-ps8r.onrender.com";

function showTab(name) {
  document.getElementById('analyzeSection').classList.add('hidden');
  document.getElementById('searchSection').classList.add('hidden');
  document.getElementById(name + 'Section').classList.remove('hidden');
  document.getElementById('tab-analyze').className = 'btn ' + (name === 'analyze' ? 'grad' : 'bg-gray-700') + ' flex-1';
  document.getElementById('tab-search').className = 'btn ' + (name === 'search' ? 'grad' : 'bg-gray-700') + ' flex-1';
}

function getRole() {
  try {
    return JSON.parse(atob(token.split('.')[1])).rol || 'User';
  } catch (e) {
    return 'User';
  }
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
  btn.textContent = 'Conectando... (puede tardar 50 s)';
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
      var waBtn = c.whatsapp ? '<a class="btn bg-green-600 text-sm" target="_blank" href="https://wa.me/' + c.whatsapp.replace(/[^0-9]/g, '') + '"><i class="fab fa-whatsapp mr-2"></i>WhatsApp</a>' : '';
      var revealBtn = admin ? '<button class="btn grad text-sm reveal-btn">Revelar Identidad</button>' : '<span class="text-xs text-gray-500 self-center">Solo Admin</span>';
      
      card.innerHTML =
        '<div class="flex justify-between items-start gap-4 mb-4">' +
          '<h3 class="font-bold gtext text-lg">' + c.perfil_ciego_id + '</h3>' +
          '<span class="chip text-green-300">' + c.match_porcentaje + '% MATCH</span>' +
        '</div>' +
        '<div class="mb-4">' + (c.skills_coincidentes || []).map(function (s) { return '<span class="chip text-green-300">' + s + '</span>'; }).join('') + '</div>' +
        '<p class="text-sm text-gray-300 italic mb-5 bg-black bg-opacity-20 p-3 rounded-lg">' + (c.cv_redactado || 'Sin perfil redactado') + '</p>' +
        '<div class="flex gap-3 flex-wrap items-center">' + waBtn + revealBtn + '</div>' +
        '<div class="identity-box hidden mt-5 p-4 rounded-xl bg-black bg-opacity-30 text-xs"></div>';
      box.appendChild(card);
      
      var rb = card.querySelector('.reveal-btn');
      if (rb) {
        rb.addEventListener('click', function () {
          revelarIdentidad(c.perfil_ciego_id, rb);
        });
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
    
    var html = '<p class="text-purple-300 font-bold mb-2">Identidad revelada por: ' + data.identidad_revelada_por + '</p>';
    if (data.whatsapp) {
      html += '<p class="text-green-400 mb-2 font-bold"><i class="fab fa-whatsapp mr-1"></i> WhatsApp: ' + data.whatsapp + '</p>';
    }
    html += '<pre class="whitespace-pre-wrap text-gray-300 mt-3 bg-black bg-opacity-40 p-3 rounded-lg">' + data.texto_original_completo + '</pre>';
    
    box.innerHTML = html;
    btn.disabled = true;
    btn.textContent = 'Revelado';
    btn.className = 'btn bg-green-600 text-sm cursor-not-allowed';
  } catch (e) {
    box.textContent = 'Error: ' + String(e.message);
  }
}
</script>
</body>
</html>
"""