from fastapi import APIRouter, Depends, Query
from ...core.auth_dependency import get_current_user
from ... models import User, UserRead
from typing import List, Optional
from sqlmodel import Session, select
from ... db import get_session


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

@router.get("/users", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
    order_by: str = Query("id"),
    order_dir: str = Query("asc")
):
    query = select(User)

    # Filtrado
    if search:
        query = query.where(User.email.contains(search))

    # Orden
    if order_by not in User.__table__.columns.keys():
        order_by = "id"
    column = getattr(User, order_by)
    if order_dir == "desc":
        column = column.desc()
    query = query.order_by(column)

    # Paginación
    query = query.offset(skip).limit(limit)

    results = session.exec(query).all()
    return results