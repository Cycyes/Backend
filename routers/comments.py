from fastapi import APIRouter, Depends, HTTPException
from database import crud, models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user, AUTH_USERNAME
from pydantic import BaseModel
import requests

router = APIRouter()

class deleteCommentInfo(BaseModel):
    comment_id: str
class postCommentIn(BaseModel):
    content: str
    postId: int

# 更新点赞状态
@router.get("/updateLikeComment/{commentId}")
async def updateLikeComment(commentId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    # 验证是否存在该评论
    db_comment = crud.get_comment(db=db, comment_id=commentId)
    if not db_comment:
        return { "code": 1, "msg": "该commentId对应的动态不存在", "data": {} }
    
    # 更新点赞状态
    new_like_list = db_comment.like_list

    if current_user.stu_id in db_comment.like_list.split(','):
        if db_comment.like_list != "" and current_user.stu_id == db_comment.like_list.split(',')[0]:
            if len(db_comment.like_list.split(',')) == 1:
                new_like_list = new_like_list.replace(current_user.stu_id, "")
            else:
                new_like_list = new_like_list.replace(current_user.stu_id + ",", "")
        else:
            new_like_list = db_comment.like_list.replace("," + current_user.stu_id, "")
        msg = "取消点赞"
    else:
        if db_comment.like_list != "":
            new_like_list += ("," + str(current_user.stu_id))
        else:
            new_like_list += (str(current_user.stu_id))
        msg = "点赞"

    crud.update_like_comment(db=db, comment_id=commentId, new_like_list=new_like_list)

    data = {}

    try:
        data['likeNum'] = 0 if db_comment.like_list == "" else len(db_comment.like_list.split(','))
    except:
        data['likeNum'] = 0

    data['isLiked'] = bool(current_user.stu_id in db_comment.like_list.split(','))

    # 产生点赞消息
    if msg == "点赞":
        db_notice = crud.create_likenotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=db_comment.stu_id, post_id=-1, comment_id=commentId)

    return { "code": 0, "msg": msg, "data": data }

# 发布评论
@router.post("/postComment")
async def postComment(r: postCommentIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    # 查询是否存在postId对应的动态
    db_memory = crud.get_memory(db=db, post_id=r.postId)
    if not db_memory:
        return { "code": 1, "msg": "postId对应的动态不存在", "data": {} }

    c = crud.create_comment(db=db, post_id=r.postId, content=r.content, stu_id=current_user.stu_id)

    # 将评论加到帖子的评论区
    new_comment_list = db_memory.comment_list
    if db_memory.comment_list != "":
        new_comment_list += ("," + str(c.comment_id))
    else:
        new_comment_list += (str(c.comment_id))
    crud.update_memory_comment(db=db, post_id=r.postId, new_comment_list=new_comment_list)

    # 产生评论消息
    db_notice = crud.create_commentnotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=db_memory.stu_id, comment_id=c.comment_id)

    return { "code": 0, "msg": "SUCCESS", "data": {} }

# 删除评论
@router.post("/deleteComment")
async def deleteComment(info: deleteCommentInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    db_comment = crud.get_comment(db = db, comment_id = info.comment_id)
    if not db_comment:
        return { "code": 1, "msg": "该commentId对应的评论不存在", "data": {} }
    
    if current_user.stu_id != AUTH_USERNAME and current_user.stu_id != db_comment.stu_id:
        return { "code": 1, "msg": "你不能删除别人的评论", "data": {} }

    # 将被删除的评论从帖子的评论列表中删除
    db_memory = crud.get_memory(db=db, post_id=db_comment.post_id)
    new_comment_list = ""
    for i in db_memory.comment_list.split(','):
        if int(i) != int(db_comment.comment_id):
            if new_comment_list != "":
                new_comment_list += ("," + str(i))
            else:
                new_comment_list += (str(i))
    crud.update_memory_comment(db=db, post_id=db_comment.post_id, new_comment_list=new_comment_list)

    data = {}
    data['deleteComment'] = crud.delete_comment(db=db, comment_id=info.comment_id)

    return {
        "code": 0,
        "msg": "删除成功",
        "data": data
    }
