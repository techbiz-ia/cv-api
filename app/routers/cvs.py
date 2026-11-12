from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import json
from datetime import datetime
from openai import OpenAI
from fastapi.responses import FileResponse

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter(prefix="/cvs", tags=["CVs"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProcesarIARequest(BaseModel):
    texto_cv: str
    whatsapp: str = ""
    archivo_pdf: str = None

def analizar_con_ia(texto: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Falta la clave de API de OpenAI en el servidor.")
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Analiza el siguiente texto de un currículum vitae para un sistema de Blind Hiring.
    1. Extrae las habilidades técnicas y blandas principales como una lista de strings.
    2. Redacta un resumen profesional breve (máximo 3 oraciones).
    3. REDACTA (reemplaza con [REDACTADO]) cualquier dato sensible como correos, teléfonos o DNI.
    
    Responde ÚNICAMENTE con un objeto JSON válido en este formato exacto:
    {{
      "habilidades": ["Habilidad 1", "Habilidad 2"],
      "resumen_redactado": "Texto del resumen con datos sensibles redactados."
    }}
    
    Texto del CV:
    {texto}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar con IA: {str(e)}")

@router.post("/procesar-ia", status_code=201)
def procesar_ia(request: ProcesarIARequest, db: Session = Depends(get_db)):
    if not request.texto_cv.strip():
        raise HTTPException(status_code=400, detail="El texto del CV no puede estar vacío.")
    
    resultado_ia = analizar_con_ia(request.texto_cv)
    perfil_ciego_id = f"cv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    nuevo_cv = CVDB(
        perfil_ciego_id=perfil_ciego_id,
        source_text="Texto pegado manualmente",
        redacted_text=resultado_ia.get("resumen_redactado", "Resumen generado por IA"),
        status="procesado",
        whatsapp=request.whatsapp or None,
        archivo_pdf=request.archivo_pdf
    )
    db.add(nuevo_cv)
    db.flush()
    
    for skill_name in resultado_ia.get("habilidades", []):
        db.add(SkillDB(skill=skill_name, cv_id=nuevo_cv.id))
    
    db.commit()
    db.refresh(nuevo_cv)
    return {"status": "procesado", "perfil_ciego_id": nuevo_cv.perfil_ciego_id, "skills_extraidas": resultado_ia.get("habilidades", []), "texto_redactado": nuevo_cv.redacted_text}

@router.post("/procesar-archivo", status_code=201)
async def procesar_archivo(file: UploadFile = File(...), whatsapp: str = Form(""), db: Session = Depends(get_db)):
    filename = file.filename.lower() if file.filename else ""
    if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .pdf, .docx o .txt")
    
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    contenido_bytes = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(contenido_bytes)
    
    contenido = ""
    try:
        if filename.endswith('.txt'):
            contenido = contenido_bytes.decode("utf-8")
        elif filename.endswith('.pdf'):
            import PyPDF2, io
            for page in PyPDF2.PdfReader(io.BytesIO(contenido_bytes)).pages:
                contenido += page.extract_text() + "\n"
        elif filename.endswith('.docx'):
            import docx, io
            contenido = "\n".join([para.text for para in docx.Document(io.BytesIO(contenido_bytes)).paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")
    
    if not contenido.strip():
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del archivo.")
    
    request = ProcesarIARequest(texto_cv=contenido, whatsapp=whatsapp, archivo_pdf=unique_filename)
    resultado_ia = analizar_con_ia(request.texto_cv)
    perfil_ciego_id = f"cv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    nuevo_cv = CVDB(
        perfil_ciego_id=perfil_ciego_id,
        source_text=f"Archivo: {unique_filename}",
        redacted_text=resultado_ia.get("resumen_redactado", "Resumen generado por IA"),
        status="procesado",
        whatsapp=request.whatsapp or None,
        archivo_pdf=unique_filename
    )
    db.add(nuevo_cv)
    db.flush()
    
    for skill_name in resultado_ia.get("habilidades", []):
        db.add(SkillDB(skill=skill_name, cv_id=nuevo_cv.id))
    
    db.commit()
    db.refresh(nuevo_cv)
    return {"status": "procesado", "perfil_ciego_id": nuevo_cv.perfil_ciego_id, "skills_extraidas": resultado_ia.get("habilidades", []), "texto_redactado": nuevo_cv.redacted_text}

@router.get("/archivo/{filename}")
def descargar_archivo(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, media_type='application/pdf', filename=filename)

@router.get("/lista")
def listar_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CVDB).all()
    resultado = []
    for cv in cvs:
        resultado.append({
            "id": cv.id,
            "nombre_completo": cv.perfil_ciego_id or "Nombre no disponible",
            "whatsapp": cv.whatsapp,
            "email": None,
            "status": cv.status,
            "habilidades": [s.skill for s in cv.skills] if cv.skills else [],
            "experiencia_resumen": cv.redacted_text or cv.source_text or "Sin resumen disponible",
            "archivo_pdf": cv.archivo_pdf
        })
    return {"total": len(resultado), "cvs": resultado}

@router.delete("/{cv_id}", status_code=200)
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")
    if cv.archivo_pdf:
        file_path = os.path.join(UPLOAD_DIR, cv.archivo_pdf)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.delete(cv)
    db.commit()
    return {"mensaje": "CV eliminado correctamente", "id_eliminado": cv_id}