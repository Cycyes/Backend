from typing import Union
from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user, DEFAULT_ROOM_PASSWORD
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
import time

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class room(BaseModel):
    roomPwd: Union[str, None] = None
    coverUrl: str
    videoUrl: str
    roomName: str
    roomDescription: str
    roomPms: int

class joinRoom(BaseModel):
    roomId: str
    roomPwd: Union[str, None] = None

class editRoomInfo(BaseModel):
    roomId: str
    coverUrl: str
    videoUrl: str
    roomName: str
    roomDescription: str
    roomPms: int
    roomPwd: Union[str, None] = None

class leaveRoomInfo(BaseModel):
    userId: str
    roomId: str

class roomMessage(BaseModel):
    roomId: str
    text: str
    image: str

class roomVideo(BaseModel):
    positionMillis: int
    shouldPlay: bool
    curTime: str
    roomId: str

# 将字符串形式的成员列表转为列表
def getMembers(user_list: str):
    ret = []
    for user in user_list.split(','):
        ret.append(user)
    return ret

def get_user_info(db: Session, user_id: str):
    user = crud.get_user(db=db, stu_id=user_id)
    if user:
        return {"stu_id": user.stu_id, "user_name": user.user_name}
    return {}

# 通过房间号取得可以查看的信息
def getRoomInfoById(roomId: str, db: Session = Depends(get_db)):
    room = crud.get_room_by_roomid(db=db, room_id=roomId)
    data = {}
    creator_info = get_user_info(db, room.creator_id)
    if creator_info:
        data['roomId'] = room.id
        data['ownerId'] = room.creator_id
        data['coverUrl'] = room.cover_url
        data['videoUrl'] = room.video_url
        data['roomName'] = room.name
        data['roomPms'] = bool(room.pms)
        data['roomDescription'] = room.description
        data['members'] = getMembers(room.user_list)
    return data

# 创建房间
@router.post("/createRoom")
async def postMemory(r: room, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if r.roomPwd == None:
        r.roomPwd = DEFAULT_ROOM_PASSWORD

    room = crud.create_room(
        db=db, 
        creator_id=current_user.stu_id, 
        password=get_password_hash(r.roomPwd), 
        cover_url=r.coverUrl, 
        video_url=r.videoUrl, 
        name=r.roomName, 
        description=r.roomDescription, 
        pms=r.roomPms)

    return { "code": 0, "msg": "success", "data": room }

# 获取房间列表
@router.get("/rooms")
async def getAllRooms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 1
    msg = "没有房间"
    data = []

    room_list = crud.get_all_rooms(db=db)
    room_list.reverse()

    if room_list:
        code = 0
        msg = "返回成功"
        for room in room_list:
            if room.pms:
                continue
            e = {}
            try:
                e['creatorId'] = crud.get_user(db=db, stu_id=room.creator_id).stu_id
                e['creatorName'] = crud.get_user(db=db, stu_id=room.creator_id).user_name
            except:
                return { "code": 2, "msg": "房间对应用户出错", "data": data }
            e['roomId'] = room.id
            e['coverUrl'] = room.cover_url
            e['roomName'] = room.name
            e['roomDescription'] = room.description
            data.append(e)
    return { "code": code, "msg": msg, "data": data }

# 加入房间
@router.post("/joinRoom")
async def joinRooms(r: joinRoom, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "房间不存在", "data":{} }
    # pms为1时需要密码
    if room.pms:
        # 验证密码
        if not verify_password(r.roomPwd, room.password):
            return { "code": 2, "msg": "密码错误", "data":{} }
    # 更新房间的成员列表
    crud.update_room_user_list(db=db, room=room, user_id=current_user.stu_id)
    # 返回房间基础信息
    data = getRoomInfoById(roomId=r.roomId, db=db)
    return { "code": 0, "msg": "success", "data": data }

# 获取房间详情
@router.get("/getRoomInfo")
async def getRoomInfo(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return {"code": 0, "msg": "success", "data": getRoomInfoById(roomId=roomId, db=db)}

# 编辑房间信息
@router.put("/editRoom")
async def editRoom(r: editRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "房间不存在", "data":{} }
    if room.creator_id != current_user.stu_id:
        return { "code": 2, "msg": "不能修改其他人的房间信息", "data":{} }
    data = crud.update_room_info(
        db=db,
        roomId=r.roomId,
        coverUrl=r.coverUrl,
        videoUrl=r.videoUrl,
        roomName=r.roomName,
        roomDescription=r.roomDescription,
        roomPms=r.roomPms,
        roomPwd=get_password_hash(r.roomPwd)
    )
    return { "code": 0, "msg": "修改成功", "data": data }

# 接收房间所有消息
@router.get("/receiveAllRoomMessages")
async def receiveAllRoomMessages(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_room = crud.get_room_by_roomid(db=db, room_id=int(roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    message_list = db_room.message_list.split(',')
    data = []
    for i in message_list:
        db_message = crud.get_message_by_id(db=db, id=i)
        if not db_message:
            continue
        r = {}
        r["text"] = db_message.text
        r["image"] = db_message.image
        r["time"] = db_message.time
        r["id"] = db_message.id
        r["isRecall"] = db_message.is_recall
        r["userId"] = db_message.from_id

        # 获取发送者消息
        db_user = crud.get_user(db=db, stu_id=db_message.from_id)
        db_user_add_info = crud.get_user_add_info(db=db, stu_id=db_message.from_id)
        if db_user:
            if db_user.user_name_perm:
                r["userNikeName"] = db_user.user_name
        if db_user_add_info:
            if db_user_add_info.avatar_perm:
                r["userAvatar"] = db_user_add_info.avatar

        data.append(r)
    
    rec = 0 if len(data) == 0 else data[-1]["id"]

    db_rec = crud.get_rec_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_rec:
        db_rec = crud.update_rec(db=db, stu_id=db_rec.stu_id, room_id=db_rec.room_id, message_id=rec)
    else:
        db_rec = crud.create_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=rec)

    return {"code": 0, "msg": "success", "data": data}

# 接受房间未读消息
@router.get("/receiveRoomMessages")
async def receiveRoomMessages(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_room = crud.get_room_by_roomid(db=db, room_id=int(roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    rec = 0
    db_rec = crud.get_rec_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_rec:
        rec = db_rec.message_id
    else:
        db_rec = crud.create_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=0)

    message_list = db_room.message_list.split(',')
    data = []
    for i in message_list:
        db_message = crud.get_message_by_id(db=db, id=i)
        if not db_message:
            continue
        if db_message.id <= rec:
            continue
        r = {}
        r["text"] = db_message.text
        r["image"] = db_message.image
        r["time"] = db_message.time
        r["id"] = db_message.id
        r["isRecall"] = db_message.is_recall
        r["userId"] = db_message.from_id

        # 获取发送者消息
        db_user = crud.get_user(db=db, stu_id=db_message.from_id)
        db_user_add_info = crud.get_user_add_info(db=db, stu_id=db_message.from_id)
        if db_user:
            if db_user.user_name_perm:
                r["userNikeName"] = db_user.user_name
        if db_user_add_info:
            if db_user_add_info.avatar_perm:
                r["userAvatar"] = db_user_add_info.avatar

        data.append(r)
    
    rec = rec if len(data) == 0 else max(rec, data[-1]["id"])
    db_rec = crud.update_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=rec)

    return {"code": 0, "msg": "success", "data": data}


# 发送房间信息
@router.post("/sendRoomMessage")
async def sendRoomMessage(r: roomMessage, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_room = crud.get_room_by_roomid(db=db, room_id=str(r.roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    user_list = db_room.user_list.split(',')
    if current_user.stu_id not in user_list:
        return {"code": 2, "msg": "用户不在房间内", "data": {}}
    
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    db_message = crud.create_message(db=db, from_id=current_user.stu_id, to_id='r'+r.roomId, text=r.text, image=r.image, time=t, is_read=1, is_sender_delete=0, is_receiver_delete=0, is_recall=0)
    new_message_list = db_room.message_list + ',' + str(db_message.id) if db_room.message_list != "" else db_room.message_list + str(db_message.id)
    db_room = crud.update_room_message_list(db=db, room_id=r.roomId, message_list=new_message_list)
    data = {}
    data["messageId"] = db_message.id

    return {"code": 0, "msg": "success", "data": data}

# 从房间移除一个用户
@router.post("/leaveRoom")
async def leaveRoom(r: leaveRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 房主永远是user_list的首元素
    # 可以移除的情况: 房主移除别人, 普通用户自己退出
    # 当房主退出时, 需要移交房主, 直接使得下一个顺位的人成为房主
    # 当没有人在房间里, 需要删除这个房间
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "对应房间不存在", "data": {} }

    db_rec = crud.get_rec_by_stuid(db=db, stu_id=r.userId)

    # 如果当前登录用户是房主
    if room.creator_id == current_user.stu_id:
        # 如果是房主自己退出, 且房间中还有人, 将房主设置为数组中的下一个人
        if r.userId == current_user.stu_id and len(room.user_list.split(',')) > 1:
            room.creator_id = room.user_list.split(',')[1]
        # 在user_list中移除这个用户
        crud.remove_user_in_user_list(db=db, room=room, remove_id=r.userId)
        if db_rec:
            crud.delete_rec(db=db, stu_id=r.userId)
    # 如果当前登录用户与要删除的用户一致
    elif r.userId == current_user.stu_id:
        crud.remove_user_in_user_list(db=db, room=room, remove_id=r.userId)
        if db_rec:
            crud.delete_rec(db=db, stu_id=r.userId)
    else:
        return { "code": 2, "msg": "你不能移除其他用户", "data": {} }

    # 没人了要删除这个房间
    if room.user_list == "":
        crud.delete_room(db=db, room_id=r.roomId)

    if crud.get_room_by_roomid(db=db, room_id=r.roomId):
        return { "code": 0, "msg": "成员已删除", "data": room }
    else:
        return { "code": 0, "msg": "房间已删除", "data": {} }


# 更新视频进度
@router.post("/updateProgress")
async def updateProgress(r: roomVideo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not db_room:
        return {"code": 1, "msg": "对应房间不存在", "data": {}}
    if db_room.creator_id != current_user.stu_id:
        return {"code": 2, "msg": "非房主无法更新视频进度", "data": {}}
    db_room = crud.update_room_video_progress(db=db, room_id=r.roomId, video_pos_millis=r.positionMillis, video_play=r.shouldPlay, video_cur_time=r.curTime)
    return {"code": 0, "msg": "success", "data": {}}


# 获取当前视频进度
@router.get("/getProgress")
async def getProgress(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_room = crud.get_room_by_roomid(db=db, room_id=roomId)
    if not db_room:
        return {"code": 1, "msg": "对应房间不存在", "data": {}}
    data = {}
    data["videoUrl"] = db_room.video_url
    data["curTime"] = db_room.video_cur_time
    data["shouldPlay"] = bool(db_room.video_play)
    data["positionMillis"] = db_room.video_pos_millis
    return {"code": 0, "msg": "success", "data": data}
