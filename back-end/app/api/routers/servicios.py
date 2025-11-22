from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from ... db import get_session
from ...models import Servicio, ServicioRead
from typing import List, Optional   

router = APIRouter(prefix='/servicios', tags=['servicios'])

@router.post('/', status_code=201)
def create_servicio(payload: dict):
    nombre = payload.get('nombre')
    descripcion = payload.get('descripcion')
    with Session(db.engine) as session:
        s = Servicio(nombre=nombre, descripcion=descripcion)
        session.add(s)
        session.commit()
        session.refresh(s)
        return s

@router.get("/servicios", response_model=List[ServicioRead])
def listar_servicios(
    skip: int = 0,
    limit: int = Query(10, le=100),  # máximo 100 por página
    order_by: Optional[str] = Query(None, regex="^(nombre|id)$"),
    nombre: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Servicio)

    # Filtrar por nombre
    if nombre:
        query = query.where(Servicio.nombre.contains(nombre))

    # Orden dinámico
    if order_by:
        query = query.order_by(getattr(Servicio, order_by))

    # Paginación
    query = query.offset(skip).limit(limit)

    return session.exec(query).all()

@router.get('/{servicio_id}')
def get_servicio(servicio_id: int):
    with Session(db.engine) as session:
        s = session.get(Servicio, servicio_id)
        if not s:
            raise HTTPException(status_code=404, detail='Servicio not found')
        return s

@router.put('/{servicio_id}')
def update_servicio(servicio_id: int, payload: dict):
    with Session(db.engine) as session:
        s = session.get(Servicio, servicio_id)
        if not s:
            raise HTTPException(status_code=404, detail='Servicio not found')
        s.nombre = payload.get('nombre', s.nombre)
        s.descripcion = payload.get('descripcion', s.descripcion)
        session.add(s)
        session.commit()
        session.refresh(s)
        return s

@router.delete('/{servicio_id}', status_code=204)
def delete_servicio(servicio_id: int):
    with Session(db.engine) as session:
        s = session.get(Servicio, servicio_id)
        if not s:
            raise HTTPException(status_code=404, detail='Servicio not found')
        session.delete(s)
        session.commit()
        return None
