from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class follow_info(BaseModel):
    stuid: str

# current_user 关注 stuid
@router.post("/follow")
async def follow(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = {}

    # 在建立数据库的时候就将自己加入关注列表中?
    # 不能对自己执行关注操作
    if info.stuid == current_user.stu_id:
        code = 1
        msg = {"不能对自己执行该操作"}
        return {
            "code": code,
            "msg": msg
        }

    # 如果已经关注, 不做操作
    flag = False
    followings_list = crud.get_followings(db=db, stu_id=current_user.stu_id)
    if followings_list:
        code = 0
        for i in followings_list:
            if info.stuid == i.followed: 
                flag = True
                break
    if flag:
        code = 2
        msg = {"已经关注该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 建立关注关系
    db_follow = crud.create_follow(db=db, followed_id=info.stuid, follower_id=current_user.stu_id)
    msg = {"关注成功"}

    # 产生关注消息
    db_notice = crud.create_follownotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=info.stuid)

    return {
        "code": code,
        "msg": msg,
        "db_follow": db_follow
    }

# current_user 取关 stuid
@router.post("/unfollow")
async def unfollow(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = {}

    # 不能对自己执行取关操作
    if info.stuid == current_user.stu_id:
        code = 1
        msg = {"不能对自己执行该操作"}
        return {
            "code": code,
            "msg": msg
        }

    # 如果并未关注, 不做操作
    flag = False
    followings_list = crud.get_followings(db=db, stu_id=current_user.stu_id)
    if followings_list:
        code = 0
        for i in followings_list:
            if info.stuid == i.followed: 
                flag = True
                break
    if not flag:
        code = 2
        msg = {"并未关注该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 删除关注关系
    db_follow = crud.delete_follow(db=db, followed_id=info.stuid, follower_id=current_user.stu_id)
    msg = {"取关成功"}
    return {
        "code": code,
        "msg": msg,
        "db_follow": db_follow
    }