from typing import Union
from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user, DEFAULT_ROOM_PASSWORD
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
import time
from typing import Dict

router = APIRouter()

class SocketId(BaseModel):
    socketId: str

# 重构：获取匹配状态
def get_match_status(current_user_id: str, db: Session) -> Dict[str, str]:
    data = {"match": ""}

    waiting_list = crud.get_all_waitings(db=db)
    current_index = None

    for i, waiting_user in enumerate(waiting_list):
        if waiting_user.stu_id == current_user_id:
            current_index = i
            break
    
    if current_index is not None and current_index >= 1:
        data["match"] = waiting_list[current_index - 1].stu_id
    elif current_index is not None and current_index < len(waiting_list) - 1:
        data["match"] = waiting_list[current_index + 1].stu_id

    return data

# 查询匹配状态
@router.get("/queryMatch")
async def queryMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    data = get_match_status(current_user.stu_id, db)

    if data["match"] != "":
        # 更新匹配状态并创建匹配记录
        matched_user = data["match"]
        crud.delete_wait(db=db, stu_id=current_user.stu_id)
        crud.delete_wait(db=db, stu_id=matched_user)

        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db_match = crud.create_match(db=db, id0=current_user.stu_id, id1=matched_user, time=t, is_end=0)

        return {"code": 0, "msg": "success", "data": data}
    else:
        return {"code": 0, "msg": "匹配失败", "data": data}

# 结束匹配
@router.post("/endMatch")
async def endMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_user = crud.get_wait_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_user:
        crud.delete_wait(db=db, stu_id=current_user.stu_id)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 0, "msg": "用户不在匹配列表", "data": {}}


# 开始匹配
@router.post("/startMatch")
async def startMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_user = crud.get_wait_by_stuid(db=db, stu_id=current_user.stu_id)
    if not db_user:
        db_wait = crud.create_wait(db=db, stu_id=current_user.stu_id)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 0, "msg": "用户已经在匹配中", "data": {}}


# 查询匹配状态
@router.get("/queryMatch")
async def queryMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    data = {}
    data["match"] = ""

    waiting_list = crud.get_all_waitings(db=db)
    if len(waiting_list) >= 2:
        for i in range(len(waiting_list)):
            if waiting_list[i].stu_id == current_user.stu_id:
                if i >= 1:
                    data["match"] = waiting_list[i - 1].stu_id
                else:
                    data["match"] = waiting_list[i + 1].stu_id

    if data["match"] != "":
        crud.delete_wait(db=db, stu_id=current_user.stu_id)
        crud.delete_wait(db=db, stu_id=data["match"])

        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db_match = crud.create_match(db=db, id0=current_user.stu_id, id1=data["match"], time=t, is_end=0)
        return {"code": 0, "msg": "success", "data": data}
    else:
        return {"code": 0, "msg": "匹配失败", "data": data}

# 更新socketId
@router.post("/match/uploadSocketId")
async def uploadSocketId(r: SocketId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_socket = crud.get_socket_by_stuid(db=db, stu_id=current_user.stu_id)

    if db_socket:
        crud.update_socket(db=db, stu_id=current_user.stu_id, socket_id=r.socketId)
    else:
        crud.create_socket(db=db, stu_id=current_user.stu_id, socket_id=r.socketId)

    return {"code": 0, "msg": "success", "data": {}}


# 获取socketId
@router.get("/match/getSocketId/{userId}")
async def getSocketId(userId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_socket = crud.get_socket_by_stuid(db=db, stu_id=userId)

    data = {}
    if db_socket:
        data["socketId"] = db_socket.socket_id
        return {"code": 0, "msg": "success", "data": data}
    else:
        data["socketId"] = ""
        return {"code": 1, "msg": "不存在", "data": data}