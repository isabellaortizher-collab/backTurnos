# app/routers/sucursales.py
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.db import engine
from app.models import Sucursal, SucursalCreate, SucursalRead

router = APIRouter(prefix="/sucursales", tags=["sucursales"])

@router.get("/", response_model=list[SucursalRead])
def list_sucursales():
    with Session(engine) as session:
        return session.exec(select(Sucursal)).all()

@router.post("/", response_model=SucursalRead)
def create_sucursal(payload: SucursalCreate):
    with Session(engine) as session:
        suc = Sucursal.from_orm(payload)
        session.add(suc)
        session.commit()
        session.refresh(suc)
        return suc

@router.get("/{sucursal_id}", response_model=SucursalRead)
def get_sucursal(sucursal_id: int):
    with Session(engine) as session:
        s = session.get(Sucursal, sucursal_id)
        if not s:
            raise HTTPException(404, "Sucursal no encontrada")
        return s
