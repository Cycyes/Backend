from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from database import crud, models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user, canSeeThisMemory, AUTH_USERNAME
from pydantic import BaseModel
import requests

router = APIRouter()

class memoryIn(BaseModel):
    postContent: str
    isAnonymous: bool
    pms: Union[int, None] = None
    photoUrl: list

# 动态广场
# pms == 0 时, 所有人可见
# pms == 1 时, 仅互关好友可见
# pms == 2 时, 仅关注当前用户的人可见
# pms == 3 时, 仅自己可见
@router.get("/Memories")
async def getMemories(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 1
    msg = "没有动态"
    data = []
    memories_list = crud.get_memories(db=db)
    memories_list.reverse()
    if memories_list:
        code = 0
        msg = "返回成功"
        for memory in memories_list:
            if not canSeeThisMemory(db=db, current_user=current_user, memory=memory):
                continue
            e = {}

            try:
                e['userId'] = crud.get_user(db=db, stu_id=memory.stu_id).stu_id
                e['userName'] = crud.get_user(db=db, stu_id=memory.stu_id).user_name
            except:
                return { "code": 2, "msg": "动态对应用户出错", "data": data }

            db_user_add_info = crud.get_user_add_info(db=db, stu_id=memory.stu_id)
            if db_user_add_info:
                try:
                    e['userAvatar'] = db_user_add_info.avatar
                except:
                    e['userAvatar'] = ""
            else:
                e['userAvatar'] = ""
            
            if memory.photo_list:
                try:
                    e['postPhoto'] = crud.get_photo(db=db, photo_id=memory.photo_list.split(',')[0]).address
                except:
                    return { "code": 3, "msg": "动态对应照片出错", "data": data }
            else:
                e['postPhoto'] = ""

            e['postTime'] = memory.time
            e['postId'] = str(memory.post_id)
            e['likeNum'] = str(len(memory.like_list.split(','))) if memory.like_list else '0'
            e['commentNum'] = str(len(memory.comment_list.split(','))) if memory.comment_list else '0'
            e['repoNum'] = str(len(memory.repo_list.split(','))) if memory.repo_list else '0'
            e['isLiked'] = current_user.stu_id in memory.like_list.split(',')
            e['isAnonymous'] = bool(memory.is_anonymous)

            data.append(e)
    
    return { "code": code, "msg": msg, "data": data }


# 动态详情
@router.get("/Memories/{postId}")
async def getMemoryDetail(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 1
    msg = "动态号错误"
    data = {}
    memory = crud.get_memory(db=db, post_id=postId)
    if memory:
        code = 0
        msg = "返回成功"
        
        data['likeNum'] = str(len(memory.like_list.split(','))) if memory.like_list != "" else '0'
        data['repoNum'] = str(len(memory.repo_list.split(','))) if memory.repo_list != "" else '0'
        data['postTime'] = memory.time
        data['postContent'] = memory.content
        data['postPhoto'] = []
        data['isAnonymous'] = bool(memory.is_anonymous)
        data['pms'] = memory.pms

        try:
            data['userId'] = crud.get_user(db=db, stu_id=memory.stu_id).stu_id
            data['userName'] = crud.get_user(db=db, stu_id=memory.stu_id).user_name
        except:
            return { "code": 2, "msg": "动态对应用户出错", "data": data }
        
        try:
            data['userAvatar'] = crud.get_user_add_info(db=db, stu_id=memory.stu_id).avatar
        except:
            data['userAvatar'] = ""

        if memory.photo_list:
            try:
                for photo_id in memory.photo_list.split(','):
                    data['postPhoto'].append(crud.get_photo(db=db, photo_id=photo_id).address)
            except:
                return { "code": 3, "msg": "动态对应照片出错", "data": data }

        data['isLiked'] = current_user.stu_id in memory.like_list.split(',')
        data['comments'] = []
        # 有评论才能查看
        for comment_id in memory.comment_list.split(','):
            if not comment_id:
                break
            e = {}
            try:
                comment = crud.get_comment(db=db, comment_id=comment_id)
            except:
                return { "code": 4, "msg": "动态对应评论出错", "data": data }
            e['commentId'] = comment.comment_id
            e['likeNum'] = 0 if comment.like_list == "" else len(comment.like_list.split(','))
            e['isLiked'] = current_user.stu_id in comment.like_list.split(',')
            e['postTime'] = comment.time
            e['commentContent'] = comment.content
            try:
                e['userId'] = crud.get_user(db=db, stu_id=comment.stu_id).stu_id
                e['userName'] = crud.get_user(db=db, stu_id=comment.stu_id).user_name
                e['userAvatar'] = crud.get_user_add_info(db=db, stu_id=comment.stu_id).avatar
            except:
                return { "code": 5, "msg": "评论对应用户出错", "data": data }
            data['comments'].append(e)

    return { "code": code, "msg": msg, "data": data }


# 发布动态
@router.post("/Post")
async def postMemory(r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = {}

    photo_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_list.append(db_photo.photo_id)

    crud.create_memory(db=db, stu_id=current_user.stu_id, content=r.postContent, photo_url=photo_list, pms=(1 if r.pms == None else r.pms), is_anonymous=r.isAnonymous)

    return { "code": 0, "msg": "success", "data": data }

# 编辑动态
@router.put("/updateMemory/{postId}")
async def updateMemory(postId: str, r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }

    # 验证权限
    if current_user.stu_id != db_memory.stu_id:
        return { "code": 2, "msg": "非该用户的动态，没有权限修改", "data": {} }

    photo_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_list.append(db_photo.photo_id)
    
    crud.update_memory(db=db, post_id=postId, content=r.postContent, photo_url=photo_list, pms=(1 if r.pms == None else r.pms))

    return { "code": 0, "msg": "success", "data": {} }


# 删除动态
@router.get("/deleteMemory/{postId}")
async def deleteMemory(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }

    # 验证权限
    if current_user.stu_id != db_memory.stu_id and current_user.stu_id != AUTH_USERNAME:
        return { "code": 2, "msg": "非该用户的动态，没有权限删除", "data": {} }

    # 删除对应的评论
    for i in db_memory.comment_list.split(','):
        if crud.get_comment(db=db, comment_id=i):
            crud.delete_comment(db=db, comment_id=i)
    crud.delete_memory(db=db, post_id=postId)

    return {"code": 0, "msg": "success", "data": {}}


# 更新点赞状态
@router.get("/updateLikeMemory/{postId}")
async def updateLikeMemory(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }
    
    # 更新点赞状态
    new_like_list = db_memory.like_list

    if current_user.stu_id in db_memory.like_list.split(','):
        if db_memory.like_list != "" and current_user.stu_id == db_memory.like_list.split(',')[0]:
            if len(db_memory.like_list.split(',')) == 1:
                new_like_list = new_like_list.replace(current_user.stu_id, "")
            else:
                new_like_list = new_like_list.replace(current_user.stu_id + ",", "")
        else:
            new_like_list = db_memory.like_list.replace("," + current_user.stu_id, "")
        msg = "取消点赞"
    else:
        if db_memory.like_list != "":
            new_like_list += ("," + str(current_user.stu_id))
        else:
            new_like_list += (str(current_user.stu_id))
        msg = "点赞"

    crud.update_like_memory(db=db, post_id=postId, new_like_list=new_like_list)

    data = {}

    try:
        data['likeNum'] = 0 if db_memory.like_list == "" else len(db_memory.like_list.split(','))
    except:
        data['likeNum'] = 0
    
    data['isLiked'] = bool(current_user.stu_id in db_memory.like_list.split(','))

    # 产生点赞消息
    if msg == "点赞":
        db_notice = crud.create_likenotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=db_memory.stu_id, post_id=postId, comment_id=-1)
    
    return { "code": 0, "msg": msg, "data": data }
