 
from argon2 import PasswordHasher
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

ph = PasswordHasher()

def hash_password(password:str):
    return ph.hash(password)


def create_access_token(user_id:int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub" : str(user_id),
        "exp" : expire
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_password(
    password: str,
    hash_password: str
) -> bool:

    try:
        ph.verify(hash_password, password)
        return True
    except Exception:
        return False
       