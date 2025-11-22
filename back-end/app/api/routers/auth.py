from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ... import db
from ...models import User
from ...core.security import get_password_hash, verify_password, create_access_token
from ...core.rate_limiter import check_rate
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Utils para obtener usuario desde el token ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    with Session(db.engine) as session:
        user = session.get(User, int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

# --- Registro ---
@router.post("/register")
def register(payload: dict, request: Request):
    ip = request.client.host
    check_rate(f"auth_register:{ip}", settings.RATE_LIMIT_AUTH_PER_MIN)

    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    with Session(db.engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            email=email,
            full_name=full_name or "",
            hashed_password=get_password_hash(password),
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return {"id": new_user.id, "email": new_user.email}

# --- Login ---
@router.post("/login")
def login(payload: dict, request: Request):
    ip = request.client.host
    check_rate(f"auth_login:{ip}", settings.RATE_LIMIT_AUTH_PER_MIN)

    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    with Session(db.engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token, expires_in = create_access_token(subject=str(user.id))
        return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}

# --- Usuario actual ---
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }

