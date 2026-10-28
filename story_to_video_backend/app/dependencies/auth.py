from h11._abnf import status_code
from alembic.autogenerate.render import _user_defined_render
from pydantic import HttpUrl
import jwt

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

def get_current_user(
    access_token : str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):

    if not access_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail ="Not authorised"
        )

    try:

        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                 status_code = 401,
                detail ="invalid token"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail = "invalid or  expired token"
        )

    user = db.get(User, int(user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail = "user not found"
        )

    return user