# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import create_db_and_tables
from .api.routers import auth, users, turnos, servicios, health, sucursales
from .core.errors import register_exception_handlers
from .core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Sistema de Turnos", version="0.2.0", debug=True)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Límite de solicitudes excedido!"})

cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "API Sistema de Turnos funcionando"}

# ---- Routers ----
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(turnos.router)       
app.include_router(servicios.router)         # /servicios ...
app.include_router(users.router)             # según defina su router
app.include_router(health.router)
app.include_router(sucursales.router)        # /sucursales ...

# ---- Startup ----
@app.on_event("startup")
def on_startup():
    print("Creando tablas en la base de datos si no existen...")
    create_db_and_tables()
