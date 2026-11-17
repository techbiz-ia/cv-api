from app.database import engine, Base
from app.models import usuarios, cv  # Importamos los modelos para que SQLAlchemy los conozca

print("🔄 Creando tablas en la base de datos local...")
Base.metadata.create_all(bind=engine)
print("✅ ¡Base de datos local inicializada correctamente con todas las columnas!")