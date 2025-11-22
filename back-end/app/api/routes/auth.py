from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select
from ... import db
from ...models import User
from ...core.security import get_password_hash, verify_password, create_access_token
from ...core.rate_limiter import check_rate
from ...core.config import settings

router = APIRouter()

@router.post('/register')
def register(payload: dict, request: Request):
    ip = request.client.host
    check_rate(f"auth_register:{ip}", settings.RATE_LIMIT_AUTH_PER_MIN)
    email = payload.get('email')
    password = payload.get('password')
    full_name = payload.get('full_name')
    with Session(db.engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            raise HTTPException(status_code=400, detail='Email already registered')
        new_user = User(email=email, full_name=full_name or '', hashed_password=get_password_hash(password))
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}

@router.post('/login')
def login(payload: dict, request: Request):
    ip = request.client.host
    check_rate(f"auth_login:{ip}", settings.RATE_LIMIT_AUTH_PER_MIN)
    email = payload.get('email')
    password = payload.get('password')
    with Session(db.engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        token, expires_in = create_access_token(subject=str(user.id))
        return {'access_token': token, 'token_type': 'bearer', 'expires_in': expires_in}
