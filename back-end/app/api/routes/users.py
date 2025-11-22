from fastapi import APIRouter, Depends
from ...core.auth_dependency import get_current_user
from ... models import User
from sqlmodel import Session
from ... import db


router = APIRouter()

@router.get('/me')
def me(user = Depends(get_current_user)):
    user_id = user.id
    with Session(db.engine) as session:
        u = session.get(User, user_id)
        if not u:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        return {"id": u.id, "email": u.email, "full_name": u.full_name}
