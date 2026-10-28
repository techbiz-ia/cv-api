from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json
import jwt
from openai import OpenAI
import pypdf
import docx
from io import BytesIO

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key_cambiar_en_produccion")
ALGORITHM = "HS256"

def validar_token_y_obtener_rol(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")
    return payload

class CVProcesarRequest(BaseModel):
    texto_cv: str
    whatsapp: str | None = None

class CVUpdateRequest(BaseModel):
    texto_cv: str | None = None
    status: str | None = None

class BusquedaRequisitos(BaseModel):
    skills_requeridas: list[str]
    min_match_porcentaje: int = 50

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extraer_texto_de_archivo(file: UploadFile) -> str:
    filename = file.filename.lower()
    contenido = file.file.read()
    if filename.endswith('.txt'):
        return contenido.decode('utf-8')
    elif filename.endswith('.pdf'):
        reader = pypdf.PdfReader(BytesIO(contenido))
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto.strip()
    elif filename.endswith('.docx'):
        doc = docx.Document(BytesIO(contenido))
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    else:
        raise ValueError("Formato no soportado. Usa .pdf, .docx o .txt")

def procesar_cv_background(cv_id: int, texto_original: str, whatsapp: str | None = None):
    db = SessionLocal()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extrae skills y redacta el CV en formato JSON: {\"skills\": [], \"texto_redactado\": \"\"}"},
                {"role": "user", "content": texto_original}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        respuesta_ia = json.loads(response.choices[0].message.content)
        
        cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
        if cv:
            cv.redacted_text = respuesta_ia.get("texto_redactado", "")
            cv.status = "procesado"
            cv.whatsapp = whatsapp
            cv.redacted_count = max(0, len(texto_original) - len(respuesta_ia.get("texto_redactado", "")))
            for skill_nombre in respuesta_ia.get("skills", []):
                db.add(SkillDB(skill=skill_nombre, cv_id=cv.id))
            db.commit()
            print(f"✅ CV {cv_id} procesado exitosamente en background")
    except Exception as e:
        print(f"❌ Error procesando CV {cv_id} en background: {str(e)}")
        cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
        if cv:
            cv.status = "error"
            db.commit()
    finally:
        db.close()

@router.post("/cvs/procesar-ia")
async def procesar_cv(request: CVProcesarRequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    texto_original = request.texto_cv
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extrae skills y redacta el CV en formato JSON: {\"skills\": [], \"texto_redactado\": \"\"}"},
                {"role": "user", "content": texto_original}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        respuesta_ia = json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar con IA: {str(e)}")

    nuevo_cv = CVDB(
        perfil_ciego_id=f"cv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        source_text=texto_original,
        redacted_text=respuesta_ia.get("texto_redactado", ""),
        status="procesado",
        redacted_count=max(0, len(texto_original) - len(respuesta_ia.get("texto_redactado", ""))),
        whatsapp=request.whatsapp
    )
    db.add(nuevo_cv)
    db.flush()
    for skill_nombre in respuesta_ia.get("skills", []):
        db.add(SkillDB(skill=skill_nombre, cv_id=nuevo_cv.id))
    db.commit()
    db.refresh(nuevo_cv)

    return {
        "mensaje": "CV procesado y guardado con IA real", 
        "cv_id": nuevo_cv.id, 
        "skills_extraidas": respuesta_ia.get("skills", []),
        "texto_redactado": respuesta_ia.get("texto_redactado", "")
    }

@router.post("/cvs/procesar-archivo")
async def procesar_archivo_cv(
    file: UploadFile = File(...),
    whatsapp: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        texto_extraido = extraer_texto_de_archivo(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")
        
    if not texto_extraido or len(texto_extraido.strip()) < 10:
        raise HTTPException(status_code=400, detail="El archivo está vacío o no se pudo extraer texto legible.")

    nuevo_cv = CVDB(
        perfil_ciego_id=f"cv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        source_text=texto_extraido,
        redacted_text="",
        status="pendiente",
        redacted_count=0,
        whatsapp=whatsapp
    )
    db.add(nuevo_cv)
    db.commit()
    db.refresh(nuevo_cv)
    
    background_tasks.add_task(procesar_cv_background, nuevo_cv.id, texto_extraido, whatsapp)
    
    return {
        "mensaje": "Archivo recibido y en proceso de análisis", 
        "cv_id": nuevo_cv.id,
        "status": "pendiente",
        "nombre_archivo": file.filename
    }

@router.get("/cvs/")
def obtener_todos_los_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CVDB).all()
    resultado = []
    for cv in cvs:
        skills = db.query(SkillDB).filter(SkillDB.cv_id == cv.id).all()
        resultado.append({
            "id": cv.id,
            "perfil_ciego_id": cv.perfil_ciego_id,
            "texto_original": cv.source_text,
            "texto_redactado": cv.redacted_text,
            "status": cv.status,
            "skills": [s.skill for s in skills],
            "whatsapp": cv.whatsapp
        })
    return resultado

@router.get("/cvs/{cv_id}")
def obtener_cv_por_id(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv: 
        raise HTTPException(status_code=404, detail="CV no encontrado")
    skills = db.query(SkillDB).filter(SkillDB.cv_id == cv.id).all()
    return {
        "id": cv.id, 
        "perfil_ciego_id": cv.perfil_ciego_id,
        "texto_original": cv.source_text, 
        "texto_redactado": cv.redacted_text,
        "status": cv.status, 
        "skills": [s.skill for s in skills],
        "whatsapp": cv.whatsapp
    }

@router.get("/cvs/perfil/{perfil_ciego_id}/identidad")
def revelar_identidad(perfil_ciego_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo un Administrador puede revelar identidades.")

    cv = db.query(CVDB).filter(CVDB.perfil_ciego_id == perfil_ciego_id).first()
    if not cv: 
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    print(f"🔓 AUDITORÍA | Admin: {payload.get('sub')} | Perfil: {perfil_ciego_id} | Hora: {datetime.utcnow()}")

    return {
        "perfil_ciego_id": cv.perfil_ciego_id,
        "identidad_revelada_por": payload.get("sub"),
        "texto_original_completo": cv.source_text,
        "whatsapp": cv.whatsapp,
        "nota": "Acción registrada en la auditoría del sistema."
    }

@router.post("/cvs/buscar-candidatos")
def buscar_candidatos(requisitos: BusquedaRequisitos, db: Session = Depends(get_db)):
    cvs_procesados = db.query(CVDB).filter(CVDB.status == "procesado").all()
    candidatos_encontrados = []
    skills_requeridas_lower = [skill.lower() for skill in requisitos.skills_requeridas]
    total_requeridas = len(skills_requeridas_lower)
    
    for cv in cvs_procesados:
        skills_cv = db.query(SkillDB).filter(SkillDB.cv_id == cv.id).all()
        skills_cv_lower = [s.skill.lower() for s in skills_cv]
        skills_coincidentes = [skill for skill in skills_requeridas_lower if skill in skills_cv_lower]
        match_porcentaje = int((len(skills_coincidentes) / total_requeridas) * 100) if total_requeridas > 0 else 0
            
        if match_porcentaje >= requisitos.min_match_porcentaje:
            candidatos_encontrados.append({
                "perfil_ciego_id": cv.perfil_ciego_id,
                "match_porcentaje": match_porcentaje,
                "skills_coincidentes": skills_coincidentes,
                "todas_las_skills_del_cv": [s.skill for s in skills_cv],
                "cv_redactado": cv.redacted_text,
                "whatsapp": cv.whatsapp
            })
            
    candidatos_encontrados.sort(key=lambda x: x["match_porcentaje"], reverse=True)
    return {"total_encontrados": len(candidatos_encontrados), "candidatos": candidatos_encontrados}

@router.put("/cvs/{cv_id}")
def actualizar_cv(cv_id: int, request: CVUpdateRequest, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv: 
        raise HTTPException(status_code=404, detail="CV no encontrado")
    if request.texto_cv is not None: 
        cv.source_text = request.texto_cv
    if request.status is not None: 
        cv.status = request.status
    db.commit()
    db.refresh(cv)
    return {"mensaje": "CV actualizado exitosamente", "cv": cv.id}

@router.delete("/cvs/{cv_id}")
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv: 
        raise HTTPException(status_code=404, detail="CV no encontrado")
    db.delete(cv)
    db.commit()
    return {"mensaje": f"CV {cv_id} eliminado exitosamente"}