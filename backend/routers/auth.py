from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr, ValidationError
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
import re
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import logging

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = int(os.environ.get('TOKEN_EXPIRE_MINUTES', '20'))

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str
    message: str


class EmailValidator(BaseModel):
    email: EmailStr


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def validate_password(password: str):
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")


def authenticate_user(email: str, password: str, db: Session):
    try:
        validated_email = EmailValidator(email=email).email
    except ValidationError:
        logging.warning("Failed login attempt with invalid email format.")
        return None

    user = db.query(Users).filter(Users.email == validated_email).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        logging.warning("Failed login attempt: incorrect password.")
        return None
    return user


def create_access_token(email: str, user_id: int, expires_delta: timedelta) -> str:
    payload = {
        "sub": email,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid email or password.')
        return {'email': email, 'id': user_id}
    except jwt.InvalidTokenError:
        logging.error("Token validation failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid email or password.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register(db: db_dependency, create_user_request: CreateUserRequest):
    validate_password(create_user_request.password)

    existing_user = db.query(Users).filter(Users.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Unable to create account. Try another email.")

    create_user_model = Users(
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {"message": "Account created successfully", "userId": create_user_model.id}


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # ✅ form-data for Swagger
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm uses `username` field — we treat it as email
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        logging.warning("Unauthorized login attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        email=user.email,
        user_id=user.id,
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    )
    logging.info(f"User with ID {user.id} logged in successfully.")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
    }