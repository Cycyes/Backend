from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Union
from jose import jwt
from database import crud
from sqlalchemy.orm import Session
from dependencies import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, Token, pwd_context
from pydantic import BaseModel

router = APIRouter()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class CustomException(HTTPException):
    def __init__(self, status_code, detail):
        super().__init__(status_code=status_code, detail=detail)

class CustomException(HTTPException):
    def __init__(self, status_code, detail):
        super().__init__(status_code=status_code, detail=detail)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user(db=db, stu_id=form_data.username)
        if not db_user:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )
        ...
    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库错误",
        )
    except PyJWTError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌生成失败",
        )
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发生未知错误",
        )