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
    print("✅ Tablas verificadas.")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN IF NOT EXISTS whatsapp VARCHAR;"))
            conn.commit()
    except Exception as e:
        print(f"⚠️ Info whatsapp: {e}")
    yield

app = FastAPI(title="Nexus Inclusivo API", version="11.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["https://cv-api-1-ps8r.onrender.com"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nexus Inclusivo · Reclutamiento del Futuro</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0a0a0f 0%,#1a1a2e 50%,#0f0f1e 100%);color:#e2e8f0;min-height:100vh;position:relative;overflow-x:hidden}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 20% 50%,rgba(99,102,241,0.1) 0%,transparent 50%),radial-gradient(circle at 80% 80%,rgba(139,92,246,0.1) 0%,transparent 50%);pointer-events:none;z-index:0}
.container{max-width:1200px;margin:0 auto;padding:40px 32px;position:relative;z-index:1}
.header{background:rgba(18,18,26,0.95);backdrop-filter:blur(20px);border-bottom:2px solid rgba(99,102,241,0.3);padding:20px 0;position:sticky;top:0;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,0.5)}
.header-content{max-width:1200px;margin:0 auto;padding:0 32px;display:flex;justify-content:space-between;align-items:center}
.logo{display:flex;align-items:center;gap:16px}
.logo-icon{width:56px;height:56px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 30px rgba(99,102,241,0.6);animation:pulse-glow 2s ease-in-out infinite}
@keyframes pulse-glow{0%,100%{box-shadow:0 0 30px rgba(99,102,241,0.6)}50%{box-shadow:0 0 50px rgba(99,102,241,0.9)}}
.logo-icon i{color:white;font-size:28px}
.logo-text{font-size:26px;font-weight:900;background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-size:200% 200%;animation:gradient-shift 3s ease infinite}
@keyframes gradient-shift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.user-info{display:flex;align-items:center;gap:16px}
.user-badge{background:rgba(99,102,241,0.15);border:2px solid rgba(99,102,241,0.4);padding:12px 20px;border-radius:12px;font-size:15px;font-weight:700;display:flex;align-items:center;gap:10px}
.user-badge i{color:#10b981;font-size:18px}
.btn-logout{background:transparent;border:2px solid rgba(148,163,184,0.3);color:#94a3b8;padding:12px 20px;border-radius:12px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.3s}
.btn-logout:hover{background:rgba(239,68,68,0.15);color:#f87171;border-color:rgba(239,68,68,0.5)}
.card{background:rgba(30,41,59,0.7);backdrop-filter:blur(20px);border:2px solid rgba(99,102,241,0.2);border-radius:20px;padding:40px;margin-bottom:32px;transition:all 0.3s}
.card:hover{border-color:rgba(99,102,241,0.5);box-shadow:0 8px 40px rgba(99,102,241,0.2)}
.card-title{font-size:28px;font-weight:800;margin-bottom:12px;color:#f1f5f9}
.card-subtitle{font-size:15px;color:#94a3b8;margin-bottom:32px}
.field-label{display:block;font-size:14px;font-weight:600;color:#cbd5e1;margin-bottom:10px}
.field-label i{color:#818cf8;margin-right:8px}
.input{width:100%;padding:14px 18px;background:rgba(15,23,42,0.8);border:2px solid rgba(99,102,241,0.2);border-radius:12px;color:#f1f5f9;font-size:15px;outline:none;transition:all 0.3s;margin-bottom:20px}
.input:focus{border-color:#6366f1;box-shadow:0 0 0 4px rgba(99,102,241,0.15)}
.btn{padding:14px 28px;border-radius:12px;font-weight:700;font-size:15px;cursor:pointer;border:none;color:white;transition:all 0.3s;width:100%;display:inline-flex;align-items:center;justify-content:center;gap:10px;position:relative;overflow:hidden}
.btn::before{content:'';position:absolute;top:50%;left:50%;width:0;height:0;border-radius:50%;background:rgba(255,255,255,0.3);transform:translate(-50%,-50%);transition:width 0.6s,height 0.6s}
.btn:hover::before{width:400px;height:400px}
.btn:hover{transform:translateY(-3px)}
.btn-primary{background:linear-gradient(135deg,#667eea,#764ba2);box-shadow:0 8px 30px rgba(99,102,241,0.4)}
.btn-success{background:linear-gradient(135deg,#10b981,#059669);box-shadow:0 8px 30px rgba(16,185,129,0.4)}
.btn-secondary{background:rgba(71,85,105,0.8);border:2px solid rgba(148,163,184,0.3)}
.btn-sm{padding:10px 18px;font-size:13px;width:auto}
.tabs{display:flex;gap:12px;margin-bottom:32px}
.tab{flex:1;padding:16px 24px;background:rgba(30,41,59,0.7);border:2px solid rgba(99,102,241,0.2);color:#94a3b8;font-weight:700;font-size:15px;cursor:pointer;border-radius:12px;transition:all 0.3s}
.tab.active{background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-color:transparent;box-shadow:0 8px 30px rgba(99,102,241,0.4)}
.hidden{display:none!important}
.text-center{text-align:center}
.text-muted{color:#94a3b8}
.text-error{color:#ef4444;font-size:13px}
.mb-4{margin-bottom:16px}
.mt-4{margin-top:16px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-bottom:40px}
.stat-box{background:rgba(30,41,59,0.7);backdrop-filter:blur(20px);border:2px solid rgba(99,102,241,0.2);border-radius:16px;padding:32px;text-align:center;transition:all 0.3s}
.stat-box:hover{transform:translateY(-8px);border-color:#6366f1;box-shadow:0 12px 40px rgba(99,102,241,0.3)}
.stat-icon{font-size:36px;color:#818cf8;margin-bottom:12px}
.stat-value{font-size:42px;font-weight:900;background:linear-gradient(135deg,#667eea,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.stat-label{font-size:14px;color:#94a3b8;font-weight:600}
.login-container{max-width:450px;margin:80px auto}
.login-icon{width:72px;height:72px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:18px;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;box-shadow:0 8px 30px rgba(99,102,241,0.5)}
.login-icon i{color:white;font-size:32px}
.divider{display:flex;align-items:center;gap:16px;margin:24px 0;color:#64748b;font-size:12px;font-weight:600}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(99,102,241,0.3),transparent)}
.link{color:#818cf8;text-decoration:none;font-weight:700;font-size:14px}
.link:hover{text-decoration:underline}
.user-card{background:rgba(15,23,42,0.8);border:2px solid rgba(99,102,241,0.2);border-radius:16px;padding:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;margin-bottom:16px;transition:all 0.3s}
.user-card:hover{border-color:rgba(99,102,241,0.5);transform:translateY(-4px);box-shadow:0 8px 30px rgba(99,102,241,0.2)}
.user-name{font-size:17px;font-weight:700;color:#f1f5f9;margin-bottom:6px}
.user-date{font-size:13px;color:#94a3b8}
.role-badge{padding:6px 14px;border-radius:8px;font-size:13px;font-weight:700}
.role-admin{background:rgba(139,92,246,0.25);color:#a78bfa;border:2px solid rgba(139,92,246,0.4)}
.role-user{background:rgba(59,130,246,0.25);color:#60a5fa;border:2px solid rgba(59,130,246,0.4)}
.chat-widget{position:fixed;bottom:32px;right:32px;z-index:1000}
.chat-toggle{width:70px;height:70px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);border:none;color:white;font-size:32px;cursor:pointer;box-shadow:0 8px 40px rgba(99,102,241,0.6);transition:all 0.3s;animation:chat-pulse 2s ease-in-out infinite}
@keyframes chat-pulse{0%,100%{box-shadow:0 8px 40px rgba(99,102,241,0.6)}50%{box-shadow:0 8px 60px rgba(99,102,241,0.9)}}
.chat-toggle:hover{transform:scale(1.1);box-shadow:0 12px 50px rgba(99,102,241,0.8)}
.chat-box{position:absolute;bottom:85px;right:0;width:400px;height:520px;background:rgba(30,41,59,0.95);backdrop-filter:blur(20px);border:2px solid rgba(99,102,241,0.3);border-radius:20px;display:none;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.chat-box.active{display:flex}
.chat-header{padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:20px 20px 0 0;color:white;font-weight:700;font-size:17px}
.chat-messages{flex:1;padding:20px;overflow-y:auto}
.chat-message{margin-bottom:16px}
.chat-message.user{text-align:right}
.chat-bubble{display:inline-block;padding:12px 18px;border-radius:16px;max-width:80%;font-size:14px;line-height:1.6}
.chat-message.bot .chat-bubble{background:rgba(15,23,42,0.8);color:#e2e8f0;border-bottom-left-radius:4px}
.chat-message.user .chat-bubble{background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-bottom-right-radius:4px}
.chat-input-area{padding:16px;border-top:2px solid rgba(99,102,241,0.2);display:flex;gap:12px}
.chat-input{flex:1;padding:12px 16px;background:rgba(15,23,42,0.8);border:2px solid rgba(99,102,241,0.3);border-radius:12px;color:#e2e8f0;font-size:14px;outline:none}
.chat-send{padding:12px 20px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:12px;color:white;cursor:pointer;font-size:15px;font-weight:700}
.wa-float{position:fixed;bottom:32px;left:32px;width:70px;height:70px;border-radius:50%;background:linear-gradient(135deg,#25D366,#128C7E);display:flex;align-items:center;justify-content:center;color:white;font-size:32px;box-shadow:0 8px 40px rgba(37,211,102,0.6);z-index:999;text-decoration:none;transition:all 0.3s}
.wa-float:hover{transform:scale(1.1);box-shadow:0 12px 50px rgba(37,211,102,0.8)}
</style>
</head>
<body>
<header class="header">
<div class="header-content">
<div class="logo">
<div class="logo-icon"><i class="fas fa-brain"></i></div>
<div class="logo-text">Nexus Inclusivo</div>
</div>
<div id="authStatus" class="hidden user-info">
<div class="user-badge"><i class="fas fa-shield-alt"></i><span id="userRole">Admin</span></div>
<button class="btn-logout" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Salir</button>
</div>
</div>
</header>

<div class="container">
<section id="loginSection">
<div class="login-container">
<div class="card">
<div class="text-center mb-4">
<div class="login-icon"><i class="fas fa-lock"></i></div>
<h2 class="card-title text-center">Iniciar sesión</h2>
<p class="card-subtitle text-center">Accede a tu cuenta</p>
</div>
<label class="field-label">Usuario</label>
<input id="loginUser" class="input" placeholder="tu.usuario">
<label class="field-label">Contraseña</label>
<input id="loginPass" class="input" type="password" placeholder="••••••••">
<button id="loginBtn" class="btn btn-primary" onclick="login()">Ingresar al sistema</button>
<p id="loginError" class="hidden text-error mt-4 text-center"></p>
<div class="divider">o</div>
<p class="text-center text-muted" style="font-size:14px;">¿Eres candidato? <a href="#" class="link" onclick="showRegisterForm();return false;">Regístrate aquí</a></p>
</div>

<div id="registerForm" class="card hidden">
<div class="text-center mb-4">
<div class="login-icon" style="background:linear-gradient(135deg,#10b981,#059669);"><i class="fas fa-user-plus"></i></div>
<h2 class="card-title text-center">Crear cuenta</h2>
<p class="card-subtitle text-center">Regístrate como candidato</p>
</div>
<label class="field-label">Nombre de usuario</label>
<input id="regUser" class="input" placeholder="ej. juan.perez">
<label class="field-label">Contraseña</label>
<input id="regPass" class="input" type="password" placeholder="Mínimo 6 caracteres">
<button id="regBtn" class="btn btn-success" onclick="register()">Registrarme</button>
<p id="regError" class="hidden text-error mt-4 text-center"></p>
<p id="regSuccess" class="hidden mt-4 text-center" style="color:#10b981;font-weight:700;"></p>
<div class="divider">o</div>
<p class="text-center text-muted" style="font-size:14px;">¿Ya tienes cuenta? <a href="#" class="link" onclick="showLoginForm();return false;">Inicia sesión</a></p>
</div>
</div>
</section>

<section id="dashboard" class="hidden">
<div class="stats-grid">
<div class="stat-box">
<div class="stat-icon"><i class="fas fa-file-alt"></i></div>
<div class="stat-value" id="statTotalCVs">0</div>
<div class="stat-label">CVs en el Sistema</div>
</div>
<div class="stat-box">
<div class="stat-icon"><i class="fas fa-magic"></i></div>
<div class="stat-value" id="statProcesados">0</div>
<div class="stat-label">Procesados con IA</div>
</div>
<div class="stat-box">
<div class="stat-icon"><i class="fas fa-tags"></i></div>
<div class="stat-value" id="statSkills">0</div>
<div class="stat-label">Habilidades Extraídas</div>
</div>
</div>

<div id="adminView" class="hidden">
<div class="tabs">
<button id="tab-analyze" class="tab active" onclick="showTab('analyze')"><i class="fas fa-file-alt"></i> Analizar CV</button>
<button id="tab-search" class="tab" onclick="showTab('search')"><i class="fas fa-search"></i> Buscar</button>
<button id="tab-users" class="tab" onclick="showTab('users')"><i class="fas fa-users"></i> Usuarios</button>
</div>

<div id="analyzeSection" class="card">
<h2 class="card-title">Procesar Currículum</h2>
<p class="card-subtitle">Analiza un CV con inteligencia artificial</p>
<label class="field-label"><i class="fas fa-file-upload"></i> Archivo (PDF, DOCX, TXT)</label>
<input id="cvFile" type="file" accept=".pdf,.docx,.txt" class="input">
<label class="field-label"><i class="fab fa-whatsapp"></i> WhatsApp (opcional)</label>
<input id="cvWhatsapp" class="input" placeholder="+54 9 ...">
<label class="field-label"><i class="fas fa-paste"></i> O pega el texto</label>
<textarea id="cvText" rows="5" class="input" placeholder="Pega aquí el contenido del CV..."></textarea>
<button id="analyzeBtn" class="btn btn-success" onclick="procesarCV()"><i class="fas fa-magic"></i> Procesar con IA</button>
<p id="analyzeError" class="hidden text-error mt-4 text-center"></p>
<div id="analyzeResult" class="hidden mt-4 text-center"></div>
</div>

<div id="searchSection" class="card hidden">
<h2 class="card-title">Buscar Candidatos</h2>
<p class="card-subtitle">Encuentra profesionales con Blind Hiring</p>
<label class="field-label"><i class="fas fa-tags"></i> Habilidades (separadas por coma)</label>
<input id="searchSkills" class="input" placeholder="Python, FastAPI, AWS">
<label class="field-label"><i class="fas fa-percent"></i> Coincidencia mínima (%)</label>
<input id="searchMinMatch" type="number" value="50" class="input">
<button class="btn btn-primary" onclick="buscarCandidatos()"><i class="fas fa-search"></i> Buscar</button>
<p id="searchError" class="hidden text-error mt-4 text-center"></p>
<div id="searchResults" class="mt-4"></div>
</div>

<div id="usersSection" class="card hidden">
<h2 class="card-title">Gestión de Usuarios</h2>
<p class="card-subtitle">Administra los usuarios registrados</p>
<button class="btn btn-primary" onclick="cargarUsuarios()" style="width:auto;padding:12px 24px;margin-bottom:24px;"><i class="fas fa-sync-alt"></i> Actualizar lista</button>
<div id="usersList"></div>
</div>
</div>

<div id="candidateView" class="hidden">
<div class="card" style="max-width:600px;margin:0 auto;">
<div class="text-center mb-4">
<div class="login-icon"><i class="fas fa-user-astronaut"></i></div>
<h2 class="card-title">¡Bienvenido!</h2>
<p class="card-subtitle">Sube tu currículum de forma anónima y segura</p>
</div>
<label class="field-label"><i class="fas fa-file-upload"></i> Sube tu CV</label>
<input id="candCvFile" type="file" accept=".pdf,.docx,.txt" class="input">
<label class="field-label"><i class="fab fa-whatsapp"></i> Tu WhatsApp (opcional)</label>
<input id="candWhatsapp" class="input" placeholder="+54 9 ...">
<button id="candAnalyzeBtn" class="btn btn-primary" onclick="procesarCVCandidato()"><i class="fas fa-paper-plane"></i> Enviar CV</button>
<p id="candError" class="hidden text-error mt-4 text-center"></p>
<div id="candResult" class="hidden mt-4 text-center" style="color:#10b981;font-weight:700;"></div>
</div>
</div>
</section>
</div>

<div class="chat-widget">
<button class="chat-toggle" onclick="toggleChat()"><i class="fas fa-comments"></i></button>
<div class="chat-box" id="chatBox">
<div class="chat-header"><i class="fas fa-robot"></i> Asistente Virtual</div>
<div class="chat-messages" id="chatMessages">
<div class="chat-message bot">
<div class="chat-bubble">¡Hola! 👋 Soy el asistente de Nexus Inclusivo. ¿En qué puedo ayudarte?</div>
</div>
</div>
<div class="chat-input-area">
<input id="chatInput" class="chat-input" placeholder="Escribe tu consulta..." onkeypress="if(event.key==='Enter')sendChat()">
<button class="chat-send" onclick="sendChat()"><i class="fas fa-paper-plane"></i></button>
</div>
</div>
</div>

<a class="wa-float" href="https://wa.me/5492993293669" target="_blank" title="Contacto"><i class="fab fa-whatsapp"></i></a>

<script>
var token="";
var API_URL="https://cv-api-1-ps8r.onrender.com";

function showRegisterForm(){
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
}

function showLoginForm(){
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('regError').classList.add('hidden');
    document.getElementById('regSuccess').classList.add('hidden');
}

async function register(){
    var user=document.getElementById('regUser').value.trim();
    var pass=document.getElementById('regPass').value.trim();
    var err=document.getElementById('regError');
    var success=document.getElementById('regSuccess');
    var btn=document.getElementById('regBtn');
    err.classList.add('hidden');
    success.classList.add('hidden');
    if(!user||!pass){
        err.textContent='Completa todos los campos.';
        err.classList.remove('hidden');
        return;
    }
    if(pass.length<6){
        err.textContent='La contraseña debe tener al menos 6 caracteres.';
        err.classList.remove('hidden');
        return;
    }
    btn.disabled=true;
    btn.textContent='Creando cuenta...';
    try{
        var res=await fetch(API_URL+'/usuarios/',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({nombre:user,password:pass,rol:"User"})
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error al crear la cuenta.');
        success.textContent='✅ ¡Cuenta creada con éxito!';
        success.classList.remove('hidden');
        document.getElementById('regUser').value='';
        document.getElementById('regPass').value='';
        setTimeout(function(){
            showLoginForm();
            document.getElementById('loginUser').value=user;
        },2000);
    }catch(e){
        err.textContent=String(e.message);
        err.classList.remove('hidden');
    }finally{
        btn.disabled=false;
        btn.textContent='Registrarme';
    }
}

async function login(){
    var user=document.getElementById('loginUser').value;
    var pass=document.getElementById('loginPass').value;
    var err=document.getElementById('loginError');
    var btn=document.getElementById('loginBtn');
    err.classList.add('hidden');
    if(!user||!pass){
        err.textContent='Completa todos los campos.';
        err.classList.remove('hidden');
        return;
    }
    btn.disabled=true;
    btn.textContent='Conectando...';
    var body=new URLSearchParams();
    body.append('username',user);
    body.append('password',pass);
    try{
        var res=await fetch(API_URL+'/usuarios/login',{
            method:'POST',
            headers:{'Content-Type':'application/x-www-form-urlencoded'},
            body:body
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Credenciales incorrectas');
        token=data.access_token;
        var role=getRole();
        document.getElementById('userRole').textContent=role==='Admin'?'Administrador':'Candidato';
        document.getElementById('loginSection').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
        document.getElementById('authStatus').classList.remove('hidden');
        if(role==='Admin'){
            document.getElementById('adminView').classList.remove('hidden');
            document.getElementById('candidateView').classList.add('hidden');
        }else{
            document.getElementById('adminView').classList.add('hidden');
            document.getElementById('candidateView').classList.remove('hidden');
        }
    }catch(e){
        err.textContent=String(e.message);
        err.classList.remove('hidden');
    }finally{
        btn.disabled=false;
        btn.textContent='Ingresar al sistema';
    }
}

function logout(){
    token="";
    document.getElementById('loginSection').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('authStatus').classList.add('hidden');
}

function getRole(){
    try{
        return JSON.parse(atob(token.split('.')[1])).rol||'User';
    }catch(e){
        return 'User';
    }
}

function showTab(name){
    document.getElementById('analyzeSection').classList.add('hidden');
    document.getElementById('searchSection').classList.add('hidden');
    document.getElementById('usersSection').classList.add('hidden');
    document.getElementById(name+'Section').classList.remove('hidden');
    document.getElementById('tab-analyze').className=name==='analyze'?'tab active':'tab';
    document.getElementById('tab-search').className=name==='search'?'tab active':'tab';
    document.getElementById('tab-users').className=name==='users'?'tab active':'tab';
    if(name==='users') cargarUsuarios();
}

async function procesarCV(){
    var file=document.getElementById('cvFile').files[0];
    var texto=document.getElementById('cvText').value.trim();
    var whatsapp=document.getElementById('cvWhatsapp').value.trim();
    var btn=document.getElementById('analyzeBtn');
    var err=document.getElementById('analyzeError');
    var out=document.getElementById('analyzeResult');
    err.classList.add('hidden');
    out.classList.add('hidden');
    if(!file&&!texto){
        err.textContent='Sube un archivo o pega el texto.';
        err.classList.remove('hidden');
        return;
    }
    btn.disabled=true;
    btn.textContent='Procesando...';
    try{
        var res;
        if(file){
            var fd=new FormData();
            fd.append('file',file);
            fd.append('whatsapp',whatsapp);
            res=await fetch(API_URL+'/cvs/procesar-archivo',{
                method:'POST',
                headers:{'Authorization':'Bearer '+token},
                body:fd
            });
        }else{
            res=await fetch(API_URL+'/cvs/procesar-ia',{
                method:'POST',
                headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
                body:JSON.stringify({texto_cv:texto,whatsapp:whatsapp})
            });
        }
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error al procesar');
        out.textContent=data.status==='pendiente'?'✅ Archivo recibido. Procesando...':'✅ CV procesado correctamente.';
        out.classList.remove('hidden');
    }catch(e){
        err.textContent=String(e.message);
        err.classList.remove('hidden');
    }finally{
        btn.disabled=false;
        btn.innerHTML='<i class="fas fa-magic"></i> Procesar con IA';
    }
}

async function procesarCVCandidato(){
    var file=document.getElementById('candCvFile').files[0];
    var whatsapp=document.getElementById('candWhatsapp').value.trim();
    var btn=document.getElementById('candAnalyzeBtn');
    var err=document.getElementById('candError');
    var out=document.getElementById('candResult');
    err.classList.add('hidden');
    out.classList.add('hidden');
    if(!file){
        err.textContent='Por favor, selecciona un archivo.';
        err.classList.remove('hidden');
        return;
    }
    btn.disabled=true;
    btn.textContent='Enviando...';
    try{
        var fd=new FormData();
        fd.append('file',file);
        fd.append('whatsapp',whatsapp);
        var res=await fetch(API_URL+'/cvs/procesar-archivo',{
            method:'POST',
            headers:{'Authorization':'Bearer '+token},
            body:fd
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error al procesar');
        out.textContent='✅ ¡CV enviado con éxito!';
        out.classList.remove('hidden');
        document.getElementById('candCvFile').value='';
        document.getElementById('candWhatsapp').value='';
    }catch(e){
        err.textContent=String(e.message);
        err.classList.remove('hidden');
    }finally{
        btn.disabled=false;
        btn.innerHTML='<i class="fas fa-paper-plane"></i> Enviar CV';
    }
}

async function buscarCandidatos(){
    var raw=document.getElementById('searchSkills').value;
    var min=parseInt(document.getElementById('searchMinMatch').value)||50;
    var err=document.getElementById('searchError');
    var box=document.getElementById('searchResults');
    err.classList.add('hidden');
    if(!raw.trim()){
        err.textContent='Ingresa al menos una habilidad.';
        err.classList.remove('hidden');
        return;
    }
    var skills=raw.split(',').map(function(s){return s.trim();}).filter(function(s){return s.length;});
    box.innerHTML='<p class="text-muted mt-4 text-center"><i class="fas fa-spinner fa-spin"></i> Buscando...</p>';
    try{
        var res=await fetch(API_URL+'/cvs/buscar-candidatos',{
            method:'POST',
            headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
            body:JSON.stringify({skills_requeridas:skills,min_match_porcentaje:min})
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error al buscar');
        box.innerHTML='';
        if(!data.total_encontrados){
            box.innerHTML='<p class="text-muted mt-4 text-center">No se encontraron candidatos.</p>';
            return;
        }
        var admin=getRole()==='Admin';
        data.candidatos.forEach(function(c){
            var card=document.createElement('div');
            card.className='user-card';
            var skillsHtml=(c.skills_coincidentes||[]).map(function(s){return '<span style="background:rgba(99,102,241,0.2);padding:6px 12px;border-radius:8px;font-size:12px;margin:3px;display:inline-block;">'+s+'</span>';}).join('');
            var waBtn=c.whatsapp?'<a class="btn btn-sm" style="background:#25D366;" target="_blank" href="https://wa.me/'+c.whatsapp.replace(/[^0-9]/g,'')+'"><i class="fab fa-whatsapp"></i> WhatsApp</a>':'';
            var revealBtn=admin?'<button class="btn btn-sm btn-primary reveal-btn"><i class="fas fa-unlock"></i> Revelar</button>':'';
            card.innerHTML='<div style="flex:1;"><div style="font-size:16px;font-weight:700;margin-bottom:6px;">'+c.perfil_ciego_id+' <span style="background:rgba(16,185,129,0.25);color:#10b981;padding:6px 12px;border-radius:8px;font-size:12px;margin-left:8px;">'+c.match_porcentaje+'% match</span></div><div style="margin-bottom:10px;">'+skillsHtml+'</div><div style="background:rgba(15,23,42,0.8);padding:14px;border-radius:10px;font-size:13px;color:#94a3b8;font-style:italic;">'+(c.cv_redactado||'Sin perfil')+'</div></div><div style="display:flex;gap:10px;margin-top:16px;">'+waBtn+revealBtn+'</div><div class="hidden identity-box"></div>';
            box.appendChild(card);
            var rb=card.querySelector('.reveal-btn');
            if(rb){
                rb.addEventListener('click',function(){revelarIdentidad(c.perfil_ciego_id,rb,card);});
            }
        });
    }catch(e){
        err.textContent=String(e.message);
        err.classList.remove('hidden');
    }
}

async function revelarIdentidad(id,btn,card){
    var box=card.querySelector('.identity-box');
    box.classList.remove('hidden');
    box.innerHTML='<p><i class="fas fa-spinner fa-spin"></i> Verificando...</p>';
    try{
        var res=await fetch(API_URL+'/cvs/perfil/'+encodeURIComponent(id)+'/identidad',{
            headers:{'Authorization':'Bearer '+token}
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Acceso denegado');
        var html='<p style="color:#818cf8;font-weight:700;margin-bottom:10px;">Revelado por: '+data.identidad_revelada_por+'</p>';
        if(data.whatsapp){
            html+='<p style="color:#10b981;margin-bottom:10px;"><i class="fab fa-whatsapp"></i> '+data.whatsapp+'</p>';
        }
        html+='<pre style="white-space:pre-wrap;color:#cbd5e1;background:rgba(15,23,42,0.8);padding:14px;border-radius:10px;margin-top:10px;font-size:12px;">'+data.texto_original_completo+'</pre>';
        box.innerHTML=html;
        btn.disabled=true;
        btn.textContent='Revelado';
    }catch(e){
        box.innerHTML='<p style="color:#ef4444;">Error: '+String(e.message)+'</p>';
    }
}

function toggleChat(){
    document.getElementById('chatBox').classList.toggle('active');
}

async function sendChat(){
    var input=document.getElementById('chatInput');
    var message=input.value.trim();
    if(!message) return;
    var messagesContainer=document.getElementById('chatMessages');
    messagesContainer.innerHTML+='<div class="chat-message user"><div class="chat-bubble">'+message+'</div></div>';
    input.value='';
    messagesContainer.scrollTop=messagesContainer.scrollHeight;
    messagesContainer.innerHTML+='<div class="chat-message bot" id="typing"><div class="chat-bubble"><i class="fas fa-spinner fa-spin"></i> Pensando...</div></div>';
    messagesContainer.scrollTop=messagesContainer.scrollHeight;
    try{
        var headers={'Content-Type':'application/json'};
        if(token){
            headers['Authorization']='Bearer '+token;
        }
        var res=await fetch(API_URL+'/chat/ask',{
            method:'POST',
            headers:headers,
            body:JSON.stringify({message:message})
        });
        if(res.status===401){
            document.getElementById('typing').remove();
            messagesContainer.innerHTML+='<div class="chat-message bot"><div class="chat-bubble">🔒 Debes iniciar sesión para usar el chat.</div></div>';
            messagesContainer.scrollTop=messagesContainer.scrollHeight;
            return;
        }
        var data=await res.json();
        document.getElementById('typing').remove();
        messagesContainer.innerHTML+='<div class="chat-message bot"><div class="chat-bubble">'+data.response+'</div></div>';
        messagesContainer.scrollTop=messagesContainer.scrollHeight;
    }catch(e){
        document.getElementById('typing').remove();
        messagesContainer.innerHTML+='<div class="chat-message bot"><div class="chat-bubble">Error de conexión.</div></div>';
    }
}

async function cargarUsuarios(){
    var list=document.getElementById('usersList');
    list.innerHTML='<p class="text-muted text-center"><i class="fas fa-spinner fa-spin"></i> Cargando...</p>';
    try{
        var res=await fetch(API_URL+'/usuarios/',{
            headers:{'Authorization':'Bearer '+token}
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error al cargar usuarios');
        if(data.length===0){
            list.innerHTML='<p class="text-muted text-center">No hay usuarios registrados.</p>';
            return;
        }
        var html='';
        data.forEach(function(u){
            var fecha=u.fecha_creacion?new Date(u.fecha_creacion).toLocaleDateString('es-AR'):'N/A';
            var rolClass=u.rol==='Admin'?'role-admin':'role-user';
            var rolText=u.rol==='Admin'?'Admin':'Candidato';
            var nuevoRol=u.rol==='Admin'?'User':'Admin';
            
            html+='<div class="user-card">';
            html+='<div style="flex:1;">';
            html+='<div class="user-name">'+u.nombre+'</div>';
            html+='<div class="user-date">Registrado: '+fecha+'</div>';
            html+='</div>';
            html+='<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">';
            html+='<span class="role-badge '+rolClass+'">'+rolText+'</span>';
            html+='<button class="btn btn-sm btn-secondary" data-action="cambiar" data-id="'+u.id+'" data-rol="'+nuevoRol+'"><i class="fas fa-exchange-alt"></i> Cambiar</button>';
            html+='<button class="btn btn-sm" style="background:#ef4444;" data-action="eliminar" data-id="'+u.id+'" data-nombre="'+u.nombre+'"><i class="fas fa-trash"></i></button>';
            html+='</div>';
            html+='</div>';
        });
        list.innerHTML=html;
        
        list.querySelectorAll('[data-action="cambiar"]').forEach(function(btn){
            btn.addEventListener('click',function(){
                cambiarRol(btn.dataset.id,btn.dataset.rol);
            });
        });
        
        list.querySelectorAll('[data-action="eliminar"]').forEach(function(btn){
            btn.addEventListener('click',function(){
                eliminarUsuario(btn.dataset.id,btn.dataset.nombre);
            });
        });
    }catch(e){
        list.innerHTML='<p class="text-error text-center">Error: '+String(e.message)+'</p>';
    }
}

async function cambiarRol(userId,nuevoRol){
    if(!confirm('¿Cambiar rol a '+nuevoRol+'?')) return;
    try{
        var res=await fetch(API_URL+'/usuarios/'+userId+'/rol?nuevo_rol='+nuevoRol,{
            method:'PUT',
            headers:{'Authorization':'Bearer '+token}
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error');
        alert('✅ '+data.mensaje);
        cargarUsuarios();
    }catch(e){
        alert('❌ Error: '+String(e.message));
    }
}

async function eliminarUsuario(userId,nombre){
    if(!confirm('¿Eliminar a "'+nombre+'"?')) return;
    try{
        var res=await fetch(API_URL+'/usuarios/'+userId,{
            method:'DELETE',
            headers:{'Authorization':'Bearer '+token}
        });
        var data=await res.json();
        if(!res.ok) throw new Error(data.detail||'Error');
        alert('✅ '+data.mensaje);
        cargarUsuarios();
    }catch(e){
        alert('❌ Error: '+String(e.message));
    }
}

async function cargarEstadisticas(){
    try{
        var res=await fetch(API_URL+'/stats');
        var data=await res.json();
        document.getElementById('statTotalCVs').textContent=data.total_cvs;
        document.getElementById('statProcesados').textContent=data.cvs_procesados;
        document.getElementById('statSkills').textContent=data.total_skills;
    }catch(e){
        console.log('Error:',e);
    }
}
cargarEstadisticas();
</script>
</body>
</html>"""