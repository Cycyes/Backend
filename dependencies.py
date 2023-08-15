from fastapi import Depends, HTTPException, status
from database.database import SessionLocal
from pydantic import BaseModel
from typing import Union
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from database import models, crud

SECRET_KEY = "8993bad3155361726b342e3155bb0f007714dbc141157b8ba5c3c1f9e520b257"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000
IMAGE_DIR = "images"

AUTH_USERNAME = "WHY-WON'T-YOU-DIE"
AUTH_PASSWORD = "NANO-MACHINE-SON"

DEFAULT_ROOM_PASSWORD = "ARKNIGHTS"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 通过 token 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token有错",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="jwt出错",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user(db=db, stu_id=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 对这条帖子判断当前登录用户是否可见
def canSeeThisMemory(db: Session, current_user: models.User, memory: models.Memory):
    # 先判断是否是管理员账号
    if current_user.stu_id == AUTH_USERNAME:
        return True
    isFollowed = False
    isFollowing = False
    follower_list = crud.get_followers(db=db, stu_id=current_user.stu_id)
    for i in follower_list:
        if i.follower == memory.stu_id:
            isFollowed = True
    following_list = crud.get_followings(db=db, stu_id=current_user.stu_id)
    for i in following_list:
        if i.followed == memory.stu_id:
            isFollowing = True
    # 判断是否互关
    if memory.pms == 1 and (not isFollowed or not isFollowing):
        return False
    # 判断是否为粉丝
    if memory.pms == 2 and not isFollowing:
        return False
    # 判断是否仅自己
    if memory.pms == 3:
        return False
    return True