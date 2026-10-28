from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ( 
    create_access_token,
    hash_password,
    verify_password
)
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserCreateRequest,
    UserResponse
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED, 
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = User(
        name=data.name,
        email=data.email, 
        password=hash_password(data.password),
        gender=data.gender,
        dob=data.dob,
        role=data.role,
        status="Active"
    )
 
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "User registered successfully"}

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    return {
        "success": True, 
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token") 
    
    
    return {"message": "Logout success"}

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User)).all()
    user_list = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "status": u.status
        }
        for u in users
    ]
    return {"success": True, "users": user_list}

@router.post("/users")
def create_user(
    data: UserCreateRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=data.name,
        email=data.email,
        role=data.role,
        password=hash_password("password123"), # default password
        status="Active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "message": "User created successfully"}