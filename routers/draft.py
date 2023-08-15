from typing import Union
from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time

router = APIRouter()

class draft(BaseModel):
    postContent: str
    photoUrl: list
    pms: int
    isAnonymous: int
    draftId: Union[int, None] = None

class DraftId(BaseModel):
    draftId: str

# drafts 草稿列表
@router.get("/drafts")
async def getDrafts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    data = []
    draft_list = crud.get_drafts_by_stu_id(db=db, stu_id=current_user.stu_id)
    for i in draft_list:
        if i.is_posted == 0:
            r = {}
            r["draftId"] = str(i.id)
            r["content"] = i.content
            r["time"] = i.time
            r["pms"] = i.pms
            r["isAnonymous"] = i.is_anonymous
            r["photoUrl"] = []
            photo_list = i.photo_list.split(',')
            for i in photo_list:
                try:
                    r["photoUrl"].append(crud.get_photo(db=db, photo_id=int(i)).address)
                except:
                    continue
            print(photo_list)
            data.append(r)
    return {"code": 0, "msg": "success", "data": data}
    

# 创建草稿
@router.post("/createDraft")
async def createDraft(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    data = {}
    print(r.photoUrl)
    print(len(r.photoUrl))
    photo_encode_list = []
    for i in r.photoUrl:
        print(i)
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_encode_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_encode_list.append(db_photo.photo_id)
        print(db_photo.photo_id)
    
    photo_list = ""
    for i in photo_encode_list:
        photo_list += str(i)
        photo_list += ","

    if len(photo_list) > 0:
        if photo_list[-1] == ",":
            photo_list = photo_list[0:-1]

    print(photo_list)

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.create_draft(db=db, stu_id=current_user.stu_id, content=r.postContent, photo_list=photo_list, time=t, pms=r.pms, is_anonymous=r.isAnonymous, is_posted=0)

    data["draftId"] = db_draft.id

    return {"code": 0, "msg": "success", "data": data}


# 编辑草稿
@router.post("/updateDraft")
async def updateDraft(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if r.draftId == None:
        return {"code": 1, "msg": "draft id 缺失", "data": {}}
    elif crud.get_draft_by_id(db=db, id=r.draftId) == None:
        return {"code": 2, "msg": "draft id 错误", "data": {}}
    elif crud.get_draft_by_id(db=db, id=r.draftId).stu_id != current_user.stu_id:
        return {"code": 3, "msg": "当前用户无编辑该草稿的权限", "data": {}}

    photo_encode_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_encode_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_encode_list.append(db_photo.photo_id)
    
    photo_list = ""
    for i in photo_encode_list:
        photo_list += str(i)
        photo_list += ","

    if len(photo_list) > 0:
        if photo_list[-1] == ",":
            photo_list = photo_list[0:-1]

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.update_draft(db=db, id=r.draftId, stu_id=current_user.stu_id, content=r.postContent, photo_list=photo_list, time=t, pms=r.pms, is_anonymous=r.isAnonymous, is_posted=0)

    return {"code": 0, "msg": "success", "data": {}}


# 发布草稿
@router.post("/postDraft")
async def postDraft(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_draft = crud.get_draft_by_id(db=db, id=r.draftId)

    if db_draft == None:
        return {"code": 1, "msg": "draft id 错误", "data": {}}
    elif db_draft.stu_id != current_user.stu_id:
        return {"code": 2, "msg": "当前用户无编辑该草稿的权限", "data": {}}
    
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.update_draft(db=db, id=db_draft.id, stu_id=current_user.stu_id, content=db_draft.content, photo_list=db_draft.photo_list, time=db_draft.time, pms=db_draft.pms, is_anonymous=db_draft.is_anonymous, is_posted=1)
    db_memory = crud.create_draft_memory(db=db, stu_id=current_user.stu_id, content=db_draft.content, photo_list=db_draft.photo_list, time=t, pms=db_draft.pms, is_anonymous=db_draft.is_anonymous)

    return {"code": 0, "msg": "success", "data": {}}

# 获取草稿详情
@router.get("/getDraft")
async def getDraft(draftId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_draft = crud.get_draft_by_id(db=db, id=draftId)

    if db_draft == None:
        return {"code": 1, "msg": "draft id 错误", "data": {}}
    elif db_draft.stu_id != current_user.stu_id:
        return {"code": 2, "msg": "当前用户无查看该草稿的权限", "data": {}}
    
    data = {}
    data["content"] = db_draft.content
    
    
    data["time"] = db_draft.time
    data["pms"] = db_draft.pms
    data["isAnonymous"] = db_draft.is_anonymous
    data["photoUrl"] = []

    photo_list = db_draft.photo_list.split(',')
    try:
        for i in photo_list:
            data["photoUrl"].append(crud.get_photo(db=db, photo_id=i).address)
    except:
        return { "code": 1, "msg": "草稿对应照片出错", "data": data }
    
    #print(data["photoUrl"])

    return {"code": 0, "msg": "success", "data": data}

# 删除草稿
@router.post("/deleteDraft")
def deleteDraft(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    draftId = r.draftId
    
    db_draft = crud.get_draft_by_id(db=db, id = draftId)

    if db_draft:
        crud.delete_draft(db=db, id=draftId)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 1, "msg": "该draftId对应的草稿不存在", "data": {}}
