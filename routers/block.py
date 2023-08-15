from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class BlockInfo(BaseModel):
    userId: str

# 拉黑用户
@router.post("/block")
async def blockUser(r: BlockInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = ""

    # 不能对自己执行拉黑操作
    if r.userId == current_user.stu_id:
        code = 1
        msg = {"不能对自己执行该操作"}
        return {
            "code": code,
            "msg": msg
        }

    # 如果已经拉黑, 不做操作
    flag = False
    block_list = crud.get_blocked_users(db=db, user_id=current_user.stu_id)
    if block_list:
        code = 0
        for i in block_list:
            if r.userId == i.blocked: 
                flag = True
                break
    if flag:
        code = 2
        msg = {"已经拉黑该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 建立拉黑关系
    block = crud.create_block_relation(db=db, blocker_id=current_user.stu_id, blocked_id=r.userId)
    msg = {"拉黑成功"}

    return {
        "code": code,
        "msg": msg,
        "data": block
    }

# 解除拉黑
@router.post("/cancelBlock")
async def unBlockUser(r: BlockInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = ""

    # 如果没有拉黑, 不做操作
    flag = False
    block_list = crud.get_blocked_users(db=db, user_id=current_user.stu_id)
    if block_list:
        code = 0
        for i in block_list:
            if r.userId == i.blocked: 
                flag = True
                break
    if not flag:
        code = 2
        msg = {"并未拉黑该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 删除拉黑关系
    block = crud.delete_block_relation(db=db, blocker_id=current_user.stu_id, blocked_id=r.userId)
    msg = {"解除拉黑成功"}

    return {
        "code": code,
        "msg": msg,
        "data": block
    }

# 查看黑名单
@router.get("/getBlockList")
async def getBlockList(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    block_list = crud.get_blocked_users(db=db, user_id=current_user.stu_id)
    return {
        "code": 0,
        "msg": "返回成功",
        "data": block_list
    }