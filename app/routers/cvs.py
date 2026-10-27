from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json
from openai import OpenAI

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CVProcesarRequest(BaseModel):
    texto_cv: str

class CVUpdateRequest(BaseModel):
    texto_cv: str | None = None
    status: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# FUNCIÓN AUXILIAR: Procesar CV en segundo plano
# ---------------------------------------------------------
def procesar_cv_background(cv_id: int, texto_original: str):
    """Esta función se ejecuta en segundo plano después de responder al usuario"""
    db = SessionLocal()
    try:
        # Llamar a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un experto en reclutamiento técnico. 
                    Tu tarea es extraer habilidades (skills) del texto del CV proporcionado.
                    Devuelve ÚNICAMENTE un objeto JSON válido con este formato exacto:
                    {
                      "skills": ["Habilidad 1", "Habilidad 2", "Habilidad 3"],
                      "texto_redactado": "Texto del CV con información personal redactada"
                    }
                    Si no encuentras habilidades, devuelve: {"skills": [], "texto_redactado": ""}
                    """
                },
                {
                    "role": "user", 
                    "content": texto_original
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        respuesta_ia = json.loads(result_text)
        
        # Actualizar el CV en la base de datos
        cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
        if cv:
            cv.redacted_text = respuesta_ia.get("texto_redactado", "")
            cv.status = "procesado"
            cv.redacted_count = max(0, len(texto_original) - len(respuesta_ia.get("texto_redactado", "")))
            
            # Guardar las skills
            for skill_nombre in respuesta_ia.get("skills", []):
                db.add(SkillDB(skill=skill_nombre, cv_id=cv.id))
            
            db.commit()
            print(f"✅ CV {cv_id} procesado exitosamente en background")
        
    except Exception as e:
        print(f"❌ Error procesando CV {cv_id} en background: {str(e)}")
        # Marcar como fallido
        cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
        if cv:
            cv.status = "error"
            db.commit()
    finally:
        db.close()

# ---------------------------------------------------------
# 1. CREAR: Procesar CV con Background Task (ASÍNCRONO)
# ---------------------------------------------------------
@router.post("/cvs/procesar-ia")
async def procesar_cv(
    request: CVProcesarRequest, 
    background_tasks: BackgroundTasks,  # 🔥 Este parámetro mágico permite tareas en segundo plano
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    texto_original = request.texto_cv
    
    # Crear el CV inmediatamente con status "pendiente"
    nuevo_cv = CVDB(
        perfil_ciego_id=f"cv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        source_text=texto_original,
        redacted_text="",  # Se llenará en background
        status="pendiente",  # 🔥 Status inicial
        redacted_count=0
    )
    db.add(nuevo_cv)
    db.commit()
    db.refresh(nuevo_cv)
    
    # 🔥 Lanzar la tarea en segundo plano
    background_tasks.add_task(procesar_cv_background, nuevo_cv.id, texto_original)
    
    # Responder inmediatamente al usuario
    return {
        "mensaje": "CV recibido y en proceso de análisis", 
        "cv_id": nuevo_cv.id,
        "status": "pendiente",
        "nota": "El procesamiento con IA está ocurriendo en segundo plano. Consulta GET /cvs/ para ver el resultado cuando status sea 'procesado'."
    }

# ---------------------------------------------------------
# 2. LEER: Obtener todos los CVs (ahora muestra el status)
# ---------------------------------------------------------
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
            "status": cv.status,  # 🔥 Ahora verás: "pendiente", "procesado" o "error"
            "skills": [s.skill for s in skills]
        })
    return resultado

# ---------------------------------------------------------
# 3. LEER UNO: Obtener un CV específico por ID
# ---------------------------------------------------------
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
        "skills": [s.skill for s in skills]
    }

# ---------------------------------------------------------
# 4. ACTUALIZAR
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 5. ELIMINAR
# ---------------------------------------------------------
@router.delete("/cvs/{cv_id}")
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    db.delete(cv)
    db.commit()
    return {"mensaje": f"CV {cv_id} y sus habilidades asociadas eliminados exitosamente"}