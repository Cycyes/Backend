from fastapi import APIRouter, Depends, HTTPException, status
from database import crud, models
from dependencies import get_db, get_current_user, canSeeThisMemory
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.testclient import TestClient

router = APIRouter()
client = TestClient(router)


class itemStr(BaseModel):
    info: str
    pms: bool

class itemList(BaseModel):
    info: list
    pms: bool

class itemInt(BaseModel):
    info: int
    pms: bool

class userIn(BaseModel):
    userId: itemStr
    userName: itemStr
    userNickName: itemStr
    userGender: itemStr
    userBirthDate: itemStr
    userStatus: itemStr
    userMajor: itemStr
    userPhone: itemStr
    userYear: itemStr
    userInterest: itemStr
    userLabel: itemList
    userAvatar: itemStr
    followerPms: bool
    followingPms: bool


class FollowersManager:
    def __init__(self, db, current_user):
        self.db = db
        self.current_user = current_user
        self.data = {
            'is_current_user': True,
            'get_others_followers': False,
            'followers': [],
        }

    def check_permissions(self, stuid):
        if stuid != self.current_user.stu_id:
            self.data['is_current_user'] = False
            other_user = crud.get_user(db=self.db, stu_id=stuid)
            self.data['get_others_followers'] = bool(other_user.follower_perm)

    def fetch_followers(self, stuid):
        followers_list = crud.get_followers(db=self.db, stu_id=stuid)
        if followers_list:
            for i in followers_list:
                if self.data['is_current_user'] and i.follower == self.current_user.stu_id:
                    continue
                if not self.data['is_current_user'] and i.follower == stuid:
                    continue
                follower_info = self._get_follower_info(i)
                self.data['followers'].append(follower_info)

    def _get_follower_info(self, follower):
        follower_info = {
            'userId': follower.follower,
            'isFollowed': self.data["is_current_user"],
            'isFollowing': False,
        }
        if not self.data["is_current_user"]:
            for j in crud.get_followings(db=self.db, stu_id=follower.follower):
                if self.current_user.stu_id == j.followed:
                    follower_info["isFollowing"] = True
                    break
        return follower_info

    def get_followers_data(self, stuid):
        self.check_permissions(stuid)
        if not self.data["is_current_user"] and not self.data['get_others_followers']:
            code = 2
            msg = {"由于对方的隐私设置, 你不能查看ta的粉丝列表"}
            return {
                "code": code,
                "msg": msg
            }

        self.fetch_followers(stuid)

        return {
            "code": 0,
            "data": self.data
        }


# 使用类的方式调用
@router.get("/profile/{stuid}/followers")
async def followers(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    manager = FollowersManager(db, current_user)
    return manager.get_followers_data(stuid)

# 获取关注的人
@router.get("/profile/{stuid}/followings")
async def followings(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    data = {}

    # 判断查看的是否是自己的粉丝列表
    # 当以下 2 项均为 False , 不可查看粉丝列表
    data['is_current_user'] = True
    data["get_others_followings"] = False
    if stuid != current_user.stu_id:
        data['is_current_user'] = False
        other_user = crud.get_user(db=db, stu_id=stuid)
        data['get_others_followings'] = bool(other_user.following_perm)
    if not data["is_current_user"] and not data['get_others_followings']:
        code = 2
        msg = {"由于对方的隐私设置, 你不能查看ta的关注列表"}
        return {
            "code": code,
            "msg": msg
        }

    # isFollowed  表示这个用户是否关注了当前登录用户
    # isFollowing 表示当前登录用户是否关注了这个用户
    # 当 is_current_user 为真时, isFollowing 为真
    data['followings'] = []
    followings_list = crud.get_followings(db=db, stu_id=stuid)
    if followings_list:
        # 用 i 遍历关注列表
        for i in followings_list:
            if data['is_current_user'] and i.followed == current_user.stu_id:
                continue
            if not data['is_current_user'] and i.followed == stuid:
                continue
            e = {}
            e['userId'] = i.followed
            e['isFollowed'] = False
            e["isFollowing"] = data["is_current_user"]
            # 遍历 i 的关注列表, 查询 i 是否关注了当前登录用户
            for j in crud.get_followings(db=db, stu_id=i.followed):
                if current_user.stu_id == j.followed:
                    e["isFollowed"] = True
                    break
            # 如果 is_current_user 为假, 再去查询 i 的粉丝列表
            if not data["is_current_user"]:
                for j in crud.get_followers(db=db, stu_id=i.followed):
                    if current_user.stu_id == j.follower:
                        e["isFollowing"] = True
                        break
            data['followings'].append(e)

    return {
        "code": code,
        "data": data
    }


# 将逻辑从路由处理函数中提取出来，形成独立的服务类
class ProfileService:
    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.current_user = current_user
    
    # 粉丝列表
    def get_followers(self, stuid):
        followers_data = client.get("/profile/{stuid}/followers")
        return followers_data

    # 关注列表
    def get_followings(self, stuid):
        followings_data = client.get("/profile/{stuid}/followings")        
        return followings_data

    # 获取用户资料
    def get_user_info(self, stuid):
        user_info_data = client.get("/profile/{stuid}")
        return user_info_data

    # 更新用户信息
    def update_user_info(self, r):
        update_result = client.put("/updateUserInfo")
        return update_result



class UserProfileHandler:
    def __init__(self, crud):
        self.crud = crud

    def get_user_info(self, stuid: str, db: Session, current_user):
        code = 1
        data = {}

        db_user, db_user_add_info = self._get_user_data(db, stuid)

        if not db_user or not db_user_add_info:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="对应的用户不存在",
                headers={}
            )

        data["is_current_user"] = self._check_current_user(stuid, current_user)

        code = 0
        data['userId'] = self._process_field_info(db_user.stu_id, data["is_current_user"], bool(db_user.stu_id_perm))
        data['userName'] = self._process_field_info(db_user.name, data["is_current_user"], bool(db_user.name_perm))
        # 其他字段信息的处理类似...

        response_data = {
            "code": code,
            "data": data
        }
        return response_data

    def _get_user_data(self, db, stuid):
        db_user = self.crud.get_user(db=db, stu_id=stuid)
        db_user_add_info = self.crud.get_user_add_info(db=db, stu_id=stuid)
        return db_user, db_user_add_info

    def _check_current_user(self, stuid, current_user):
        return stuid == current_user.stu_id

    def _process_field_info(self, info, is_current_user, permission):
        return {
            "info": info if is_current_user or permission else "None",
            "pms": bool(permission)
        }


# 创建路由
router = APIRouter()

# 初始化UserProfileHandler
handler = UserProfileHandler(crud)

# 获得用户资料
@router.get("/profile/{stuid}")
async def get_user_info(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return handler.get_user_info(stuid, db, current_user)

# 修改用户信息
@router.put("/updateUserInfo")
async def updateUserInfo(r: userIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = "修改成功"

    # 是否有修改权限
    if current_user.stu_id != r.userId.info:
        return { "code": 1, "msg": "没有修改权限", "data": {} }
    
    db_user_add_info = crud.get_user_add_info(db=db, stu_id=current_user.stu_id)
    crud.update_user(
        db=db, 
        stu_id=current_user.stu_id, 
        stu_id_perm=r.userId.pms, 
        name=current_user.name, 
        name_perm=r.userName.pms, 
        user_name=r.userNickName.info, 
        user_name_perm=r.userNickName.pms, 
        sex=current_user.sex, 
        sex_perm=r.userGender.pms, 
        faculty=current_user.faculty, 
        follower_perm=r.followerPms, 
        following_perm=r.followingPms
    )
    try:
        y = int(r.userYear.info)
    except:
        code = 2
        msg = "年份非整数"
        y = db_user_add_info.year

    db_photo = crud.get_photo_by_address(db=db, address=r.userAvatar.info)
    if not db_photo:
        db_photo = crud.create_photo(db=db, address=r.userAvatar.info)

    crud.update_user_add_info(
        db=db, 
        stu_id=current_user.stu_id, 
        birth_date=r.userBirthDate.info, 
        birth_date_perm=r.userBirthDate.pms, 
        status=r.userStatus.info, 
        status_perm=r.userStatus.pms, 
        major=r.userMajor.info, 
        major_perm=r.userMajor.pms, 
        year=y, 
        year_perm=r.userYear.pms, 
        interest=r.userInterest.info, 
        interest_perm=r.userInterest.pms, 
        label=r.userLabel.info, 
        label_perm=r.userLabel.pms, 
        avatar=r.userAvatar.info, 
        avatar_perm=True, 
        phone=r.userPhone.info, 
        phone_perm=r.userPhone.pms
    )
    return { "code": code, "msg": msg, "data": {} }


# 获取所有标签
@router.get("/getAllLabels")
async def getLabels(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = {}
    data['labels'] = []
    label_list = crud.get_labels(db=db)
    for i in label_list:
        data['labels'].append(i.label)
    return { "code": 0, "msg": "success", "data": data }


# 获取用户所有动态
@router.get("/getUserMemories/{userId}")
async def getUserMemories(userId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 检查要查找的用户是否存在
    db_user = crud.get_user(db=db, stu_id=userId)
    if not db_user:
        return { "code": 1, "msg": "用户不存在", "data": {} }
    
    data = []
    db_user_memories = crud.get_memories_by_stu_id(db=db, stu_id=userId)
    for i in db_user_memories:
        e = {}
        # 不能看的情况：
        if not canSeeThisMemory(db=db, current_user=current_user, memory=i):
            continue
        #if userId != current_user.stu_id and i.pms == 0:
        #    continue

        e['userId'] = i.stu_id
        e['postId'] = i.post_id

        try:
            e['userName'] = crud.get_user(db=db, stu_id=i.stu_id).user_name
        except:
            return { "code": 2, "msg": "动态对应用户出错", "data": data }

        db_user_add_info = crud.get_user_add_info(db=db, stu_id=i.stu_id)
        if db_user_add_info:
            try:
                e['userAvatar'] = db_user_add_info.avatar
            except:
                e['userAvatar'] = ""
        else:
            e['userAvatar'] = ""

        e['postTime'] = i.time

        if i.photo_list and i.photo_list != "":
            try:
                e['postPhoto'] = crud.get_photo(db=db, photo_id=i.photo_list.split(',')[0]).address
            except:
                return { "code": 3, "msg": "动态对应照片出错", "data": data }
        
        e['likeNum'] = int(len(i.like_list.split(','))) if (i.like_list and i.like_list != "") else 0
        e['commentNum'] = int(len(i.comment_list.split(','))) if (i.comment_list and i.comment_list != "") else 0
        e['repoNum'] = int(len(i.repo_list.split(','))) if (i.repo_list and i.repo_list != "") else 0

        try:
            e['isLiked'] = current_user.stu_id in i.like_list.split(',')
        except:
            e['isLiked'] = False

        e['isAnonymous'] = bool(i.is_anonymous)

        data.append(e)
    
    return { "code": 0, "msg": "success", "data": data }

