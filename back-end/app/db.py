# app/db.py
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path
from sqlalchemy import text

DB_FILE = Path(__file__).resolve().parents[1] / "turnos.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Para SQLite en local no hace falta check_same_thread si no usas async
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # Importa modelos para registrar metadata
    from . import models  # noqa: F401

    # 1) Crea tablas que no existan (user, servicio, sucursal, turno)
    SQLModel.metadata.create_all(engine)

    # 2) Asegura que la tabla 'turno' tenga la columna 'sucursal_id'
    with engine.begin() as conn:
        # Si la tabla 'turno' no existe, create_all ya la debió crear.
        cols = conn.execute(text("PRAGMA table_info('turno')")).fetchall()
        nombres = [c[1] for c in cols]  # [name for each column]
        if "sucursal_id" not in nombres:
            conn.execute(text("ALTER TABLE turno ADD COLUMN sucursal_id INTEGER"))
            # (En SQLite no añadimos FK con ALTER TABLE; no es necesario para operar)

def get_session():
    with Session(engine) as session:
        yield session


