from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlmodel import Session, select
from typing import List
from sqlalchemy import func
from fastapi.responses import JSONResponse

from ...db import get_session
from ...models import Turno, TurnoCreate, TurnoRead

router = APIRouter(prefix="/turnos", tags=["Turnos"])

@router.post("", response_model=TurnoRead, status_code=status.HTTP_200_OK)
def crear_turno(turno: TurnoCreate, session: Session = Depends(get_session)):
    nuevo_turno = Turno.from_orm(turno)
    session.add(nuevo_turno)
    session.commit()
    session.refresh(nuevo_turno)
    return nuevo_turno

@router.get("/", response_model=List[TurnoRead])
def read_turnos(
    *,
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    # contar total de registros
    total = session.exec(select(func.count()).select_from(Turno)).one()

    # obtener turnos con paginación
    turnos = session.exec(select(Turno).offset(offset).limit(limit)).all()

    # responder con cabecera
    response = JSONResponse(content=[t.dict() for t in turnos])
    response.headers["X-Total-Count"] = str(total)
    return response

@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(turno_id: int, session: Session = Depends(get_session)):
    turno = session.get(Turno, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    session.delete(turno)
    session.commit()
    return None

@router.put("/{turno_id}/asignar", response_model=TurnoRead)
def asignar_turno(turno_id: int, trabajador: str, session: Session = Depends(get_session)):
    turno = session.get(Turno, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    turno.asignadoA = trabajador
    session.add(turno)
    session.commit()
    session.refresh(turno)
    return turno

