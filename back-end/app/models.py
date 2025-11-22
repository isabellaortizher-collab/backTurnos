# app/models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# -------- User --------
class UserBase(SQLModel):
    email: str = Field(index=True)
    full_name: Optional[str] = None
    is_active: bool = True

class User(UserBase, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    turnos: List["Turno"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    class Config:
        orm_mode = True

# -------- Servicio --------
class ServicioBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None

class Servicio(ServicioBase, table=True):
    __tablename__ = "servicio"
    id: Optional[int] = Field(default=None, primary_key=True)
    turnos: List["Turno"] = Relationship(back_populates="servicio")

class ServicioCreate(ServicioBase):
    pass

class ServicioRead(ServicioBase):
    id: int
    class Config:
        orm_mode = True

# -------- Sucursal --------
class SucursalBase(SQLModel):
    nombre: str = Field(index=True, description="Nombre de la sucursal")
    direccion: Optional[str] = Field(default=None, description="Dirección exacta")
    ciudad: Optional[str] = Field(default=None, description="Ciudad donde se ubica la sucursal")
    activa: bool = Field(default=True, description="Indica si la sucursal está activa")

class Sucursal(SucursalBase, table=True):
    __tablename__ = "sucursal"
    id: Optional[int] = Field(default=None, primary_key=True)
    turnos: List["Turno"] = Relationship(back_populates="sucursal")

class SucursalCreate(SucursalBase):
    pass

class SucursalRead(SucursalBase):
    id: int
    class Config:
        orm_mode = True

# -------- Turno --------
class TurnoBase(SQLModel):
    cliente: str = Field(index=True, description="Nombre del cliente que solicita el turno")
    tipo: str = Field(description="Tipo de atención o trámite")
    hora: str = Field(description="Hora asignada al turno (HH:MM)")
    asignadoA: Optional[str] = Field(default=None, description="Empleado asignado, si aplica")

class Turno(TurnoBase, table=True):
    __tablename__ = "turno"
    id: Optional[int] = Field(default=None, primary_key=True)

    servicio_id: Optional[int] = Field(default=None, foreign_key="servicio.id")
    servicio: Optional["Servicio"] = Relationship(back_populates="turnos")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="turnos")

    sucursal_id: Optional[int] = Field(default=None, foreign_key="sucursal.id")
    sucursal: Optional["Sucursal"] = Relationship(back_populates="turnos")

class TurnoCreate(TurnoBase):
    servicio_id: Optional[int] = None
    user_id: Optional[int] = None
    sucursal_id: Optional[int] = None

class TurnoRead(TurnoBase):
    id: int
    servicio_id: Optional[int] = None
    user_id: Optional[int] = None
    sucursal_id: Optional[int] = None
    class Config:
        orm_mode = True

