from fastapi import APIRouter, Depends, HTTPException
from database import crud, models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from pydantic import BaseModel
import time
import copy

router = APIRouter()


class userIdIn(BaseModel):
    userId: str


class sendMessageIn(BaseModel):
    userId: str
    text: str
    image: str


class deleteMessageIn(BaseModel):
    messageId: int


class recallMessageIn(BaseModel):
    messageId: int

def handle_exception(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return {"code": 1, "msg": "An error occurred: " + str(e), "data": {}}
    return wrapper

def get_to_messages_by_id(db, current_user):
    msgs = crud.get_all_messages_by_to_id(db=db, to_id=current_user.stu_id)
    msgs_dict = {}
    for i in msgs:
        if i.from_id in msgs_dict.keys():
            msgs_dict[i.from_id].append({"text": i.text, "image": i.image, "time": i.time, "is_read": i.is_read, "isRecall": i.is_recall})
        else:
            msgs_dict[i.from_id] = [{"text": i.text, "image": i.image, "time": i.time, "is_read": i.is_read, "isRecall": i.is_recall}]
    return msgs_dict


def get_conversion_messages(db, current_user, userId):
    msgs_receive = list(filter(lambda x: x.is_receiver_delete == 0,
                               crud.get_all_messages_by_to_id_and_from_id(db=db, from_id=userId,
                                                                          to_id=current_user.stu_id)))
    msgs_send = list(filter(lambda x: x.is_sender_delete == 0,
                            crud.get_all_messages_by_to_id_and_from_id(db=db, from_id=current_user.stu_id,
                                                                       to_id=userId)))
    msgs = msgs_receive + msgs_send
    msgs.sort(key=lambda x: x.time, reverse=False)
    return msgs


@router.get("/chat/getMessageInfo")
@handle_exception
async def getLastMessage(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    msgs_dict = get_to_messages_by_id(db=db, current_user=current_user)
    data = []
    for from_id, value in msgs_dict.items():
        e = {}
        e["message"] = value[-1]['text'] if value[-1]['text'] != "" else "[图片]"
        e["timeStamp"] = value[-1]['time']

        e["senderUserId"] = from_id
        try:
            db_user = crud.get_user(db=db, stu_id=from_id)
            db_user_add = crud.get_user_add_info(db=db, stu_id=from_id)
            e["senderName"] = db_user.name
            e["senderAvatar"] = db_user_add.avatar
        except:
            e["senderName"] = "this user has no name"
            e["senderAvatar"] = "this user has no avatar"

        e["unreadedNum"] = 0
        for i in value:
            if i['is_read'] == 0:
                e["unreadedNum"] += 1

        data.append(e)

    return {"code": 0, "msg": "success", "data": data}


@router.post("/chat/sendMessage")
@handle_exception
async def sendMessage(r: sendMessageIn, db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_message = crud.create_message(db=db, from_id=current_user.stu_id, to_id=r.userId, text=r.text, image=r.image,
                                     time=t, is_read=0, is_sender_delete=0, is_receiver_delete=0, is_recall=0)
    return {"code": 0, "msg": "success", "data": {"id": db_message.id}}


@router.get("/chat/receiveAllMessages")
@handle_exception
async def receiveAllMessages(userId: str, db: Session = Depends(get_db),
                             current_user: models.User = Depends(get_current_user)):
    msgs = get_conversion_messages(db=db, current_user=current_user, userId=userId)

    data = []
    for i in msgs:
        is_received = (i.to_id == current_user.stu_id)

        r = {}
        r["id"] = i.id
        r["text"] = i.text
        r["image"] = i.image
        r["time"] = i.time
        r["isReceived"] = is_received
        r["isRecall"] = i.is_recall

        # 发送消息者信息
        db_user = crud.get_user(db=db, stu_id=userId)
        db_user_add_info = crud.get_user_add_info(db=db, stu_id=userId)
        if db_user:
            if db_user.user_name_perm:
                r["userNikeName"] = db_user.user_name
        if db_user_add_info:
            if db_user_add_info.avatar_perm:
                r["userAvatar"] = db_user_add_info.avatar

        data.append(r)

    return {"code": 0, "msg": "success", "data": data}


@router.post("/chat/deleteMessages")
@handle_exception
async def deleteMessages(r: userIdIn, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    msgs = get_conversion_messages(db=db, current_user=current_user, userId=r.userId)

    for i in msgs:
        if i.to_id == current_user.stu_id:
            crud.update_message(db=db, id=i.id, from_id=i.from_id, to_id=i.to_id, text=i.text, image=i.image,
                                time=i.time, is_read=i.is_read, is_sender_delete=i.is_sender_delete,
                                is_receiver_delete=1, is_recall=i.is_recall)
        elif i.from_id == current_user.stu_id:
            crud.update_message(db=db, id=i.id, from_id=i.from_id, to_id=i.to_id, text=i.text, image=i.image,
                                time=i.time, is_read=i.is_read, is_sender_delete=1,
                                is_receiver_delete=i.is_receiver_delete, is_recall=i.is_recall)

    return {"code": 0, "msg": "success", "data": {}}


@router.post("/chat/readMessageInfo")
@handle_exception
async def readMessageInfo(r: userIdIn, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    msgs = get_conversion_messages(db=db, current_user=current_user, userId=r.userId)
    for i in msgs:
        if (current_user.stu_id == i.to_id):
            crud.update_message(
                db=db,
                id=i.id,
                from_id=i.from_id,
                to_id=i.to_id,
                text=i.text,
                image=i.image,
                time=i.time,
                is_read=1,
                is_sender_delete=i.is_sender_delete,
                is_receiver_delete=i.is_receiver_delete,
                is_recall=i.is_recall
            )
    return {"code": 0, "msg": "success", "data": {}}


@router.get("/chat/receiveUnreadMessages")
@handle_exception
async def receiveUnreadMessages(userId: str, db: Session = Depends(get_db),
                                current_user: models.User = Depends(get_current_user)):
    msgs = get_conversion_messages(db=db, current_user=current_user, userId=userId)
    data = []
    for i in msgs:
        if i.to_id == current_user.stu_id:
            if not i.is_read:
                
                r = {}
                r["text"] = i.text
                r["image"] = i.image
                r["time"] = i.time
                r["id"] = i.id
                r["isRecall"] = i.is_recall

                # 发送消息者信息
                db_user = crud.get_user(db=db, stu_id=userId)
                db_user_add_info = crud.get_user_add_info(db=db, stu_id=userId)
                if db_user:
                    if db_user.user_name_perm:
                        r["userNikeName"] = db_user.user_name
                if db_user_add_info:
                    if db_user_add_info.avatar_perm:
                        r["userAvatar"] = db_user_add_info.avatar

                data.append(r)

    return {"code": 0, "msg": "success", "data": data}


@router.post("/chat/deleteMessage")
@handle_exception
async def deleteMessage(r: deleteMessageIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    db_msg = crud.get_message_by_id(db=db, id=r.messageId) # 根据messageId从数据库获取msg

    if not db_msg:
        return {"code": 2, "masg": "该消息不存在", "data": {}}

    # 检查权限
    if (current_user.stu_id == db_msg.from_id or current_user.stu_id == db_msg.to_id):
        if current_user.stu_id == db_msg.from_id:
            crud.update_message(db=db, id=db_msg.id, from_id=db_msg.from_id, to_id=db_msg.to_id, text=db_msg.text, image=db_msg.image, time=db_msg.time, is_read=db_msg.is_read, is_sender_delete=1, is_receiver_delete=db_msg.is_receiver_delete, is_recall=db_msg.is_recall) # 发送者删除
        else:
            crud.update_message(db=db, id=db_msg.id, from_id=db_msg.from_id, to_id=db_msg.to_id, text=db_msg.text, image=db_msg.image, time=db_msg.time, is_read=db_msg.is_read, is_sender_delete=db_msg.is_sender_delete, is_receiver_delete=1, is_recall=db_msg.is_recall) # 接受者删除
        return {"code": 0, "msg": "删除成功", "data": {}}
    else:
        return {"code": 1, "msg": "该消息非当前用户的消息", "data": {}}


@router.post("/chat/recallMessage")
@handle_exception
async def recallMessage(r: recallMessageIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_msg = crud.get_message_by_id(db=db, id=r.messageId) # 根据messageId从数据库获取msg

    if not db_msg:
        return {"code": 2, "masg": "该消息不存在", "data": {}}

    # 检查权限
    if current_user.stu_id == db_msg.from_id:
        crud.update_message(db=db, id=db_msg.id, from_id=db_msg.from_id, to_id=db_msg.to_id, text=db_msg.text, image=db_msg.image, time=db_msg.time, is_read=db_msg.is_read, is_sender_delete=db_msg.is_sender_delete, is_receiver_delete=db_msg.is_receiver_delete, is_recall=1)
        return {"code": 0, "msg": "撤回成功", "data":{}}
    else:
        return {"code": 1, "msg": "该消息非当前用户发出的消息", "data":{}}