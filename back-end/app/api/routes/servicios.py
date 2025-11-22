from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from ... import db
from ...models import Servicio
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

@router.get('/', response_model=List[Servicio])
def list_servicios(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), search: Optional[str] = None, sort: Optional[str] = 'id'):
    q = select(Servicio)
    with Session(db.engine) as session:
        if search:
            q = q.where(Servicio.nombre.ilike(f"%{search}%"))
        if sort:
            try:
                q = q.order_by(getattr(Servicio, sort))
            except Exception:
                pass
        offset = (page - 1) * limit
        result = session.exec(q.offset(offset).limit(limit))
        return result.all()

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
