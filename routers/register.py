from fastapi import APIRouter, Depends, HTTPException
from database import crud
from sqlalchemy.orm import Session
from dependencies import get_db
from pydantic import BaseModel
from passlib.context import CryptContext
import requests

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class registerIn(BaseModel):
    username: str
    id: str
    password: str
    sessionid: str

class updatePwdIn(BaseModel):
    id: str
    password: str
    sessionid: str

def get_password_hash(password):
    return pwd_context.hash(password)

@router.get("/register")
async def register():
    code = 0
    msg = "Please use POST method to register."
    data = {}
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

@router.post("/register")
async def register(r: registerIn, db: Session = Depends(get_db)):

    # 定义返回变量
    code = 0
    msg = "注册成功"
    data = {}

    db_user = crud.get_user(db=db, stu_id=r.id)
    if db_user:
        return {
            "code": 1,
            "msg": "用户已存在",
            "data": data
        }
        
    try:
        url = "https://1.tongji.edu.cn/api/sessionservice/session/getSessionUser"
        cookies = {"sessionid": r.sessionid}
        response = requests.get(url=url, cookies=cookies).json()
        name = response['data']['user']['name']
        sex = response['data']['user']['sex']
        faculty = response['data']['user']['facultyName']
    except:
        return {
            "code": 2,
            "msg": "sessionid错误",
            "data": data
        }

    if r.id == response['data']['uid']:
        db_user = crud.create_user(db=db, user_id=r.id, password=get_password_hash(r.password), user_name=r.username, name=name, sex=sex, faculty=faculty)
        db_user_add_info = crud.create_user_add_info(db=db, stu_id=r.id)
        data['name'] = name
        data['sex'] = sex
        data['faculty'] = faculty
        db_user_add_info["avatar"] = "https://picsum.photos/700"
    else:
        code = 3
        msg = "sessionid不匹配"

    # 关注自己
    db_follow = crud.create_follow(db=db, followed_id=r.id, follower_id=r.id)
    
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


# 修改密码
@router.post("/updatePassword")
async def updatePassword(r: updatePwdIn, db: Session = Depends(get_db)):
     # 定义返回变量
    code = 0
    msg = "修改密码成功"
    data = {}

    db_user = crud.get_user(db=db, stu_id=r.id)
    if not db_user:
        return {
            "code": 1,
            "msg": "用户不存在",
            "data": data
        }
    
    try:
        url = "https://1.tongji.edu.cn/api/sessionservice/session/getSessionUser"
        cookies = {"sessionid": r.sessionid}
        response = requests.get(url=url, cookies=cookies).json()
    except:
        return {
            "code": 2,
            "msg": "sessionid错误",
            "data": data
        }

    if r.id == response['data']['uid']:
        crud.update_user_pwd(db=db, stu_id=r.id, password=get_password_hash(r.password))
    else:
        code = 3
        msg = "sessionid不匹配"
        
    
    return {
        "code": code,
        "msg": msg,
        "data": data
    }