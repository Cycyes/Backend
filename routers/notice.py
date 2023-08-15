from fastapi import APIRouter, Depends, HTTPException, status
from database import crud, models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class noticeIn(BaseModel):
    noticeId: int
    typ: str

def get_unread_num(notice_list):

    ret = 0
    for i in notice_list:
        if i.read == 0:
            ret += 1
    return ret


def translate_type(typ):
    
    if typ == "like":
        return "点赞了你"
    elif typ == "comment":
        return "评论了你"
    elif typ == "repo":
        return "转发了你"
    elif typ == "follow":
        return "关注了你"
    else:
        return "type错误"


# 获取消息数量
@router.get("/notice/num4each")
async def getNoticeNum(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    data = {}
    
    # get all the lists
    like_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    comment_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    repo_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    follow_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)

    # return all the unread
    data['likeNum'] = get_unread_num(like_list)
    data['commentNum'] = get_unread_num(comment_list)
    data['repoNum'] = get_unread_num(repo_list)
    data['followNum'] = get_unread_num(follow_list)

    return { "code": 0, "msg": "success", "data": data }


# 获取所有系统消息
@router.get("/notice/getAllSystemNotice")
async def getAllSystemNotice(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    code = 0
    msg = "获取成功"
    data = []

    notice_list = crud.get_all_system_notice_by_stu_id(db=db, stu_id=current_user.stu_id)

    for i in notice_list:
        e = {}
        e['message'] = i.content
        e['senderName'] = i.title
        e['timeStamp'] = i.time
        e['noticeId'] = i.id
        e['readed'] = i.read
        try:
            e['senderAvatar'] = crud.get_user_add_info(db=db, stu_id=i.admin_id).avatar
        except:
            e['senderAvatar'] = "没有数据"
            code = 1
            msg = "数据对应管理员出错"

        data.append(e)
    
    return { "code": code, "msg": msg, "data": data}


# 获取通知详情
@router.get("/notice/getNoticeByType/{typ}")
async def getNoticeByType(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    code = 0
    msg = "success"

    if typ == "like":
        notice_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    elif typ == "comment":
        notice_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    elif typ == "repo":
        notice_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    elif typ == "follow":
        notice_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)
    else:
        return { "code": 1, "msg": "type错误", "data": [] }

    data = []

    for i in notice_list:
        e = {}
        
        try:
            db_user = crud.get_user(db=db, stu_id=i.from_stu_id)
            db_user_add_info = crud.get_user_add_info(db=db, stu_id=i.from_stu_id)
        except:
            code = 1
            msg = "数据库对应stu_id出错"
            continue

        e['senderName'] = db_user.name
        e['sendMessage'] = db_user.name + translate_type(typ)
        e['originPostTitle'] = ''

        try:
            e['originPostId'] = i.post_id
            e['originPostTitle'] = crud.get_memory(db=db, post_id=i.post_id).content
        except:
            try:
                e['originPostId'] = crud.get_comment(db=db, comment_id=i.comment_id).post_id
                e['originPostTitle'] = crud.get_memory(db=db, post_id=e['originPostId']).content
                
            except:
                e['originPostId'] = -1
            
        try:
            e['originCommentId'] = i.comment_id
            e['sendMessage'] += ': ' + crud.get_comment(db=db, comment_id=i.comment_id).content
        except:
            e['originCommentId'] = -1
        
        e['senderAvatar'] = db_user_add_info.avatar
        e['timeStamp'] = i.time
        e['noticeId'] = i.id
        
        data.append(e)

    return { "code": code, "msg": msg, "data": data }


# 删除选定通知
@router.post("/notice/deleteNotice")
async def deleteNotice(r: noticeIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if r.typ == "like":
        crud.delete_likenotice(db=db, id=r.noticeId)
    elif r.typ == "repo":
        crud.delete_reponotice(db=db, id=r.noticeId)
    elif r.typ == "comment":
        crud.delete_commentnotice(db=db, id=r.noticeId)
    elif r.typ == "follow":
        crud.delete_follownotice(db=db, id=r.noticeId)
    else:
        return { "code": 1, "msg": "type错误", "data": {} }

    return { "code": 0, "msg": "success", "data": {} }


# 已读各类通知
@router.post("/notice/readNoticeByType/{typ}")
async def readNoticeByType(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    code = 0
    msg = "success"

    if typ == "like":
        notice_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    elif typ == "comment":
        notice_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    elif typ == "repo":
        notice_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    elif typ == "follow":
        notice_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)
    else:
        return { "code": 1, "msg": "type错误", "data": {} }

    for i in notice_list:
        if i.read == 0:
            if typ == "like":
                db_notice = crud.update_likenotice(db=db, id=i.id, read=1)
            elif typ == "comment":
                db_notice = crud.update_commentnotice(db=db, id=i.id, read=1)
            elif typ == "repo":
                db_notice = crud.update_reponotice(db=db, id=i.id, read=1)
            elif typ == "follow":
                db_notice = crud.update_follownotice(db=db, id=i.id, read=1)
    
    return { "code": 0, "msg": "success", "data": {} }
