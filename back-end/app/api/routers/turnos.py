# app/routers/turnos.py
from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, Field, Session, select
from app.db import engine
from app.models import Turno, TurnoCreate, TurnoRead

router = APIRouter(prefix="/turnos", tags=["turnos"])

# ---------- Crear ----------
@router.post("/", response_model=TurnoRead)
def create_turno(payload: TurnoCreate):
    with Session(engine) as session:
        turno = Turno.from_orm(payload)
        session.add(turno)
        session.commit()
        session.refresh(turno)
        return turno

# ---------- Listar ----------
@router.get("/", response_model=list[TurnoRead])
def list_turnos():
    with Session(engine) as session:
        return session.exec(select(Turno)).all()

# ---------- Obtener por id ----------
@router.get("/{turno_id}", response_model=TurnoRead)
def get_turno(turno_id: int):
    with Session(engine) as session:
        t = session.get(Turno, turno_id)
        if not t:
            raise HTTPException(404, "Turno no encontrado")
        return t

# ---------- Asignar trabajador ----------
class AsignarPayload(SQLModel):
    trabajador: str = Field(description="Nombre/ID del trabajador")

@router.put("/{turno_id}/asignar", response_model=TurnoRead)
def asignar_turno(turno_id: int, payload: AsignarPayload):
    with Session(engine) as session:
        t = session.get(Turno, turno_id)
        if not t:
            raise HTTPException(404, "Turno no encontrado")
        t.asignadoA = payload.trabajador
        session.add(t)
        session.commit()
        session.refresh(t)
        return t

# ---------- Eliminar ----------
@router.delete("/{turno_id}", status_code=204)
def delete_turno(turno_id: int):
    with Session(engine) as session:
        t = session.get(Turno, turno_id)
        if not t:
            raise HTTPException(404, "Turno no encontrado")
        session.delete(t)
        session.commit()
        return

from sqlmodel import SQLModel, Field

class SucursalAssignPayload(SQLModel):
    sucursal_id: int = Field(description="ID de la sucursal a asignar")

@router.put("/{turno_id}/sucursal", response_model=TurnoRead)
def asignar_sucursal(turno_id: int, payload: SucursalAssignPayload):
    with Session(engine) as session:
        t = session.get(Turno, turno_id)
        if not t:
            raise HTTPException(404, "Turno no encontrado")
        # valida que exista la sucursal (opcional pero recomendable)
        from app.models import Sucursal
        s = session.get(Sucursal, payload.sucursal_id)
        if not s:
            raise HTTPException(404, "Sucursal no encontrada")
        t.sucursal_id = payload.sucursal_id
        session.add(t)
        session.commit()
        session.refresh(t)
        return t