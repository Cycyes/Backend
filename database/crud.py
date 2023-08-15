from sqlalchemy.orm import Session
import time

from . import models


#######################################################################################################################
################################################### USERS #############################################################
#######################################################################################################################

# get the user by stu_id in users
def get_user(db: Session, stu_id: str):
    return db.query(models.User).filter(models.User.stu_id == stu_id).first()


# get users in users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# create user in users
def create_user(db: Session, user_id: str, password: str, user_name: str, name: str, sex: int, faculty: str):
    db_user = models.User(
        stu_id=user_id, password=password, user_name=user_name, name=name, sex=sex, faculty=faculty, stu_id_perm=1,
        user_name_perm=1, follower_perm=1, following_perm=1, name_perm=1, sex_perm=1)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# update user
def update_user_pwd(db: Session, stu_id: str, password: str):
    db_user = get_user(db=db, stu_id=stu_id)
    db_user.password = password
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_add_info(db: Session, stu_id: str):
    info = models.UserAddInfo(
        stu_id=stu_id,
        birth_date="1970-1-1",
        status="编辑我的个性签名",
        major="主修专业",
        year=1970,
        interest="兴趣爱好",
        label="个性标签",
        avatar="头像",
        birth_date_perm=1,
        status_perm=1,
        major_perm=1,
        year_perm=1,
        interest_perm=1,
        label_perm=1,
        avatar_perm=1,
        phone="电话",
        phone_perm=1
    )
    db.add(info)
    db.commit()
    db.refresh(info)
    return info


# get the user by stu_id in usersaddinfo
def get_user_add_info(db: Session, stu_id: str):
    return db.query(models.UserAddInfo).filter(models.UserAddInfo.stu_id == stu_id).first()


# update the user
def update_user(db: Session,
                stu_id: str, stu_id_perm: int,
                name: str, name_perm: int,
                user_name: str, user_name_perm: int,
                sex: int, sex_perm: int, faculty: str,
                follower_perm: int, following_perm: int):
    db_user = get_user(db=db, stu_id=stu_id)
    db_user.stu_id_perm = stu_id_perm
    db_user.name = name
    db_user.name_perm = name_perm
    db_user.user_name = user_name
    db_user.user_name_perm = user_name_perm
    db_user.sex = sex
    db_user.sex_perm = sex_perm
    db_user.faculty = faculty
    db_user.follower_perm = follower_perm
    db_user.following_perm = following_perm
    db.commit()
    db.refresh(db_user)
    return db_user


# update the addition information user
def update_user_add_info(db: Session, stu_id: str,
                         birth_date: str, birth_date_perm: int,
                         status: str, status_perm: int,
                         major: str, major_perm: int,
                         year: int, year_perm: int,
                         interest: str, interest_perm: int,
                         label: list, label_perm: int,
                         avatar: str, avatar_perm: int,
                         phone: str, phone_perm: int):
    db_user = get_user_add_info(db=db, stu_id=stu_id)
    db_user.birth_date = birth_date
    db_user.birth_date_perm = birth_date_perm
    db_user.status = status
    db_user.status_perm = status_perm
    db_user.major = major
    db_user.major_perm = major_perm
    db_user.year = year
    db_user.year_perm = year_perm
    db_user.interest = interest
    db_user.interest_perm = interest_perm
    db_user.label = ""
    for i in range(len(label)):
        db_user.label = db_user.label + str(label[i]) + ("," if i < len(label) - 1 else "")
    db_user.label_perm = label_perm
    db_user.avatar = avatar
    db_user.avatar_perm = avatar_perm
    db_user.phone = phone
    db_user.phone_perm = phone_perm
    db.commit()
    db.refresh(db_user)
    return db_user


#######################################################################################################################
################################################### USERS #############################################################
#######################################################################################################################


#######################################################################################################################
################################################## FOLLOW #############################################################
#######################################################################################################################

# create a follow relation
def create_follow(db: Session, followed_id: str, follower_id: str):
    db_follow = models.Follow(followed=followed_id, follower=follower_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow


# delete a follow relation
def delete_follow(db: Session, followed_id: str, follower_id: str):
    db_follow = db.query(models.Follow).filter(
        models.Follow.followed == followed_id, models.Follow.follower == follower_id).first()
    db.delete(db_follow)
    db.commit()
    return db_follow


#######################################################################################################################
################################################## FOLLOW #############################################################
#######################################################################################################################


# get the followers
def get_followers(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Follow).filter(models.Follow.followed == stu_id).offset(skip).limit(limit).all()


# get the followings
def get_followings(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Follow).filter(models.Follow.follower == stu_id).offset(skip).limit(limit).all()


#######################################################################################################################
################################################## block  #############################################################
#######################################################################################################################

# block one user
def create_block_relation(db: Session, blocker_id: str, blocked_id: str):
    db_block = models.Block(blocker=blocker_id, blocked=blocked_id)
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

# unblock one user
def delete_block_relation(db: Session, blocker_id: str, blocked_id: str):
    db_block = db.query(models.Block).filter(
        models.Block.blocker == blocker_id, models.Block.blocked == blocked_id).first()
    db.delete(db_block)
    db.commit()
    return db_block

# get all blocked users
def get_blocked_users(db: Session, user_id: str):
    blocked_list = db.query(models.Block).filter(models.Block.blocker == user_id).all()
    return blocked_list

#######################################################################################################################
################################################## MEMORY #############################################################
#######################################################################################################################


# get all the memories
def get_memories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Memory).offset(skip).limit(limit).all()


# get all the memories by stu_id
def get_memories_by_stu_id(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Memory).filter(models.Memory.stu_id == stu_id).offset(skip).limit(limit).all()


# get memory by post_id
def get_memory(db: Session, post_id: int):
    return db.query(models.Memory).filter(models.Memory.post_id == post_id).first()


# create memory
def create_memory(db: Session, stu_id: str, content: str, photo_url: list, pms: int, is_anonymous: int):
    photo_list = ""
    for i in range(len(photo_url)):
        photo_list = photo_list + str(photo_url[i]) + ("," if i < len(photo_url) - 1 else "")
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_memory = models.Memory(content=content, time=t, photo_list=photo_list, like_list="", comment_list="",
                              repo_list="", stu_id=stu_id, pms=pms, is_anonymous=is_anonymous)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory


# create memory
def create_draft_memory(db: Session, stu_id: str, content: str, photo_list: str, time: str, pms: int, is_anonymous: int):
    
    db_memory = models.Memory(content=content, time=time, photo_list=photo_list, like_list="", comment_list="",
                              repo_list="", stu_id=stu_id, pms=pms, is_anonymous=is_anonymous)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory


# update memory
def update_memory(db: Session, post_id: int, content: str, photo_url: list, pms: int):
    db_memory = get_memory(db=db, post_id=post_id)
    db_memory.content = content
    db_memory.photo_list = ""
    for i in range(len(photo_url)):
        db_memory.photo_list = db_memory.photo_list + str(photo_url[i]) + ("," if i < len(photo_url) - 1 else "")
    db_memory.pms = pms
    db.commit()
    db.refresh(db_memory)
    return db_memory


# delete memory
def delete_memory(db: Session, post_id: int):
    db_memory = db.query(models.Memory).filter(models.Memory.post_id == post_id).first()
    db.delete(db_memory)
    db.commit()
    return db_memory


# update like memory
def update_like_memory(db: Session, post_id: int, new_like_list: str):
    db_memory = db.query(models.Memory).filter(models.Memory.post_id == post_id).first()
    db_memory.like_list = new_like_list
    db.commit()
    db.refresh(db_memory)
    return db_memory


# update posts' comments
def update_memory_comment(db: Session, post_id: int, new_comment_list: str):
    db_memory = db.query(models.Memory).filter(models.Memory.post_id == post_id).first()
    db_memory.comment_list = new_comment_list
    db.commit()
    db.refresh(db_memory)
    return db_memory


#######################################################################################################################
################################################## MEMORY #############################################################
#######################################################################################################################



#######################################################################################################################
################################################### DRAFT #############################################################
#######################################################################################################################

# get the draft by id
def get_draft_by_id(db: Session, id: int):
    return db.query(models.Draft).filter(models.Draft.id == id).first()


# get all the drafts by stu_id
def get_drafts_by_stu_id(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Draft).filter(models.Draft.stu_id == stu_id).offset(skip).limit(limit).all()


# create a draft
def create_draft(db: Session, stu_id: str, content: str, photo_list: str, time: str, pms: int, is_anonymous: int, is_posted: int = 0):
    db_draft = models.Draft(stu_id=stu_id, content=content, photo_list=photo_list, time=time, pms=pms, is_anonymous=is_anonymous, is_posted=is_posted)
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


# update a draft
def update_draft(db: Session, id: int, stu_id: str, content: str, photo_list: str, time: str, pms: int, is_anonymous: int, is_posted: int = 0):
    db_draft = get_draft_by_id(db=db, id=id)
    db_draft.stu_id = stu_id
    db_draft.content = content
    db_draft.photo_list = photo_list
    db_draft.time = time
    db_draft.pms = pms
    db_draft.is_anonymous = is_anonymous
    db_draft.is_posted = is_posted
    db.commit()
    db.refresh(db_draft)
    return db_draft

# delete a draft
def delete_draft(db: Session, id: int):
    db_draft = get_draft_by_id(db=db, id=id)
    db.delete(db_draft)
    db.commit()
    return db_draft

#######################################################################################################################
################################################### DRAFT #############################################################
#######################################################################################################################



#######################################################################################################################
################################################## PHOTOS #############################################################
#######################################################################################################################

# get photo by photo_id
def get_photo(db: Session, photo_id: int):
    return db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()


# get photo by address
def get_photo_by_address(db: Session, address: str):
    return db.query(models.Photo).filter(models.Photo.address == address).first()


# create photo by address
def create_photo(db: Session, address: str):
    db_photo = models.Photo(address=address)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


#######################################################################################################################
################################################## PHOTOS #############################################################
#######################################################################################################################


#######################################################################################################################
################################################# COMMENT #############################################################
#######################################################################################################################

# get comment by comment_id
def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()


# update like comment
def update_like_comment(db: Session, comment_id: int, new_like_list: str):
    db_comment = db.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()
    db_comment.like_list = new_like_list
    db.commit()
    db.refresh(db_comment)
    return db_comment


# delete comment
def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(
        models.Comment.comment_id == comment_id
    ).first()
    db.delete(db_comment)
    db.commit()
    return db_comment


# create comment
def create_comment(db: Session, post_id: int, content: str, stu_id: str):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_comment = models.Comment(content=content, time=t, like_list="", stu_id=stu_id, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


#######################################################################################################################
################################################# COMMENT #############################################################
#######################################################################################################################


#######################################################################################################################
################################################### LABEL #############################################################
#######################################################################################################################

# get labels
def get_labels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Label).offset(skip).limit(limit).all()


#######################################################################################################################
################################################### LABEL #############################################################
#######################################################################################################################


#######################################################################################################################
################################################# LIKENOTICE ##########################################################
#######################################################################################################################

# get all like notice by stuid
def get_likenotice(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.LikeNotice).filter(models.LikeNotice.to_stu_id == stu_id).offset(skip).limit(limit).all()


# create a like notice
def create_likenotice(db: Session, from_stu_id: str, to_stu_id: str, post_id: int, comment_id: int):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_notice = models.LikeNotice(from_stu_id=from_stu_id, to_stu_id=to_stu_id, post_id=post_id, comment_id=comment_id,
                                  time=t, read=0)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice


# delete a like notice
def delete_likenotice(db: Session, id: int):
    db_notice = db.query(models.LikeNotice).filter(models.LikeNotice.id == id).first()
    db.delete(db_notice)
    db.commit()
    return db_notice


# update a like notice
def update_likenotice(db: Session, id: int, read: int):
    db_notice = db.query(models.LikeNotice).filter(models.LikeNotice.id == id).first()
    db_notice.read = read
    db.commit()
    db.refresh(db_notice)
    return db_notice


#######################################################################################################################
################################################# LIKENOTICE ##########################################################
#######################################################################################################################


#######################################################################################################################
################################################ COMMENTNOTICE ########################################################
#######################################################################################################################

# get all comment notice by stuid
def get_commentnotice(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.CommentNotice).filter(models.CommentNotice.to_stu_id == stu_id).offset(skip).limit(
        limit).all()


# create a comment notice
def create_commentnotice(db: Session, from_stu_id: str, to_stu_id: str, comment_id: int):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_notice = models.CommentNotice(from_stu_id=from_stu_id, to_stu_id=to_stu_id, comment_id=comment_id, time=t,
                                     read=0)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice


# delete a comment notice
def delete_commentnotice(db: Session, id: int):
    db_notice = db.query(models.CommentNotice).filter(models.CommentNotice.id == id).first()
    db.delete(db_notice)
    db.commit()
    return db_notice


# update a comment notice
def update_commentnotice(db: Session, id: int, read: int):
    db_notice = db.query(models.CommentNotice).filter(models.CommentNotice.id == id).first()
    db_notice.read = read
    db.commit()
    db.refresh(db_notice)
    return db_notice


#######################################################################################################################
################################################ COMMENTNOTICE ########################################################
#######################################################################################################################


#######################################################################################################################
################################################# REPONOTICE ##########################################################
#######################################################################################################################

# get all repo notice by stuid
def get_reponotice(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.RepoNotice).filter(models.RepoNotice.to_stu_id == stu_id).offset(skip).limit(limit).all()


# delete a repo notice
def delete_reponotice(db: Session, id: int):
    db_notice = db.query(models.RepoNotice).filter(models.RepoNotice.id == id).first()
    db.delete(db_notice)
    db.commit()
    return db_notice


# update a repo notice
def update_reponotice(db: Session, id: int, read: int):
    db_notice = db.query(models.RepoNotice).filter(models.RepoNotice.id == id).first()
    db_notice.read = read
    db.commit()
    db.refresh(db_notice)
    return db_notice


#######################################################################################################################
################################################# REPONOTICE ##########################################################
#######################################################################################################################


#######################################################################################################################
################################################# FOLLOWNOTICE ########################################################
#######################################################################################################################

# get all follow notice by stuid
def get_follownotice(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.FollowNotice).filter(models.FollowNotice.to_stu_id == stu_id).offset(skip).limit(limit).all()


# create a follow notice
def create_follownotice(db: Session, from_stu_id: str, to_stu_id: str):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db_notice = models.FollowNotice(from_stu_id=from_stu_id, to_stu_id=to_stu_id, time=t, read=0)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice


# delete a follow notice
def delete_follownotice(db: Session, id: int):
    db_notice = db.query(models.FollowNotice).filter(models.FollowNotice.id == id).first()
    db.delete(db_notice)
    db.commit()
    return db_notice


# update a follow notice
def update_follownotice(db: Session, id: int, read: int):
    db_notice = db.query(models.FollowNotice).filter(models.FollowNotice.id == id).first()
    db_notice.read = read
    db.commit()
    db.refresh(db_notice)
    return db_notice


#######################################################################################################################
################################################# FOLLOWNOTICE ########################################################
#######################################################################################################################


#######################################################################################################################
################################################# SYSTEMNOTICE ########################################################
#######################################################################################################################

# get all system notices by stu_id
def get_all_system_notice_by_stu_id(db: Session, stu_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.SystemNotice).filter(models.SystemNotice.stu_id == stu_id).offset(skip).limit(limit).all()


#######################################################################################################################
################################################# SYSTEMNOTICE ########################################################
#######################################################################################################################


#######################################################################################################################
#################################################### MESSAGE ##########################################################
#######################################################################################################################

# get message by id
def get_message_by_id(db: Session, id: int):
    return db.query(models.Message).filter(models.Message.id == id).first()


# get all undeleted received messages by to_id
def get_all_messages_by_to_id(db: Session, to_id: str):
    return db.query(models.Message).filter(models.Message.to_id == to_id, models.Message.is_receiver_delete == 0).all()


# get all chat messages by to_id and from_id
def get_all_messages_by_to_id_and_from_id(db: Session, from_id: str, to_id: str):
    return db.query(models.Message).filter(models.Message.to_id == to_id, models.Message.from_id == from_id).all()
    
# create a message
def create_message(db: Session, from_id: str, to_id: str, text: str, image: str, time: str, is_read: int,
                   is_sender_delete: int, is_receiver_delete: int, is_recall: int):
    db_message = models.Message(from_id=from_id, to_id=to_id, text=text, image=image, time=time, is_read=is_read,
                                is_sender_delete=is_sender_delete, is_receiver_delete=is_receiver_delete, is_recall=is_recall)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


# update a message
def update_message(db: Session, id: int, from_id: str, to_id: str, text: str, image: str, time: str, is_read: int,
                   is_sender_delete: int, is_receiver_delete: int, is_recall: int):
    db_message = get_message_by_id(db=db, id=id)
    db_message.from_id = from_id
    db_message.to_id = to_id
    db_message.text = text
    db_message.image = image
    db_message.time = time
    db_message.is_read = is_read
    db_message.is_sender_delete = is_sender_delete
    db_message.is_receiver_delete = is_receiver_delete
    db_message.is_recall = is_recall
    db.commit()
    db.refresh(db_message)
    return db_message

#######################################################################################################################
#################################################### MESSAGE ##########################################################
#######################################################################################################################

#######################################################################################################################
##################################################### ROOMS ###########################################################
#######################################################################################################################

# create a room
def create_room(db: Session, 
                creator_id: str, 
                password: str, 
                cover_url: str, 
                video_url: str, 
                name: str, 
                description: str, 
                pms: int):
    db_room = models.Room(
        creator_id=creator_id,
        password=password, 
        cover_url=cover_url, 
        video_url=video_url, 
        name=name, 
        description=description, 
        pms=pms, 
        user_list = "",
        message_list = "",
        video_pos_millis=0,
        video_play=1,
        video_cur_time="")
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# get room list
def get_all_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

# get room by roomid
def get_room_by_roomid(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

# add one user in user_list
# 返回更新后的room
def update_room_user_list(db: Session, room: models.Room, user_id: str):
    if room.user_list == "":
        room.user_list += user_id
    else:
        room.user_list = room.user_list + "," + user_id
    db.commit()
    db.refresh(room)
    return room

# remove one user in user_list
# 返回更新后的room
def remove_user_in_user_list(db: Session, room: models.Room, remove_id: str):
    user_list = room.user_list.split(',')
    room.user_list = ""
    for user_id in user_list:
        if user_id != remove_id: 
            if room.user_list != "":
                room.user_list += ","
            room.user_list += user_id
    db.commit()
    db.refresh(room)
    return room

# edit room info
# 返回更新后的room
def update_room_info(db: Session, 
                     roomId: int,
                     coverUrl: str,
                     videoUrl: str,
                     roomName: str,
                     roomDescription: str,
                     roomPms: int,
                     roomPwd: str):
    db_room = db.query(models.Room).filter(models.Room.id == roomId).first()
    db_room.cover_url = coverUrl
    db_room.video_url = videoUrl
    db_room.name = roomName
    db_room.description = roomDescription
    db_room.pms = roomPms
    db_room.password = roomPwd
    db.commit()
    db.refresh(db_room)
    return db_room

# add one message in message_list
def update_room_message_list(db: Session, room_id: int, message_list: str):
    db_room = get_room_by_roomid(db=db, room_id=room_id)
    db_room.message_list = message_list
    db.commit()
    db.refresh(db_room)
    return db_room

# update
def update_room_video_progress(db: Session, room_id: int, video_pos_millis: int, video_play: int, video_cur_time: str):
    db_room = get_room_by_roomid(db=db, room_id=room_id)
    db_room.video_pos_millis = video_pos_millis
    db_room.video_play = video_play
    db_room.video_cur_time = video_cur_time
    db.commit()
    db.refresh(db_room)
    return db_room

# delete a room
def delete_room(db: Session, room_id: int):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    db.delete(db_room)
    db.commit()
    return db_room

#######################################################################################################################
##################################################### ROOMS ###########################################################
#######################################################################################################################



#######################################################################################################################
##################################################### WAIT ############################################################
#######################################################################################################################

def get_wait_by_stuid(db: Session, stu_id: str):
    return db.query(models.Wait).filter(models.Wait.stu_id == stu_id).first()

def get_all_waitings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Wait).offset(skip).limit(limit).all()

def create_wait(db: Session, stu_id: str):
    db_wait = models.Wait(stu_id=stu_id)
    db.add(db_wait)
    db.commit()
    db.refresh(db_wait)
    return db_wait

def delete_wait(db: Session, stu_id: str):
    db_wait = get_wait_by_stuid(db=db, stu_id=stu_id)
    db.delete(db_wait)
    db.commit()
    return db_wait


#######################################################################################################################
##################################################### WAIT ############################################################
#######################################################################################################################



#######################################################################################################################
##################################################### MATCH ###########################################################
#######################################################################################################################

def get_match_by_id1(db: Session, id1: str):
    return db.query(models.Match).filter(models.Match.id1 == id1).first()

def create_match(db: Session, id0: str, id1: str, time: str, is_end: int):
    db_match = models.Match(id0=id0, id1=id1, time=time, is_end=is_end)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

#######################################################################################################################
##################################################### MATCH ###########################################################
#######################################################################################################################



#######################################################################################################################
################################################ ROOMMESSAGEREC #######################################################
#######################################################################################################################

def get_rec_by_stuid(db: Session, stu_id: str):
    return db.query(models.RoomMessageRec).filter(models.RoomMessageRec.stu_id == stu_id).first()

def create_rec(db: Session, stu_id: str, room_id: str, message_id: int):
    db_rec = models.RoomMessageRec(stu_id=stu_id, room_id=room_id, message_id=message_id)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

def update_rec(db: Session, stu_id: str, room_id: str, message_id: int):
    db_rec = get_rec_by_stuid(db=db, stu_id=stu_id)
    db_rec.stu_id = stu_id
    db_rec.room_id = room_id
    db_rec.message_id = message_id
    db.commit()
    db.refresh(db_rec)
    return db_rec

def delete_rec(db: Session, stu_id: str):
    db_rec = get_rec_by_stuid(db=db, stu_id=stu_id)
    db.delete(db_rec)
    db.commit()
    return db_rec

#######################################################################################################################
################################################ ROOMMESSAGEREC #######################################################
#######################################################################################################################



#######################################################################################################################
#################################################### SOCKET ###########################################################
#######################################################################################################################

def get_socket_by_stuid(db: Session, stu_id: str):
    return db.query(models.Socket).filter(models.Socket.stu_id == stu_id).first()

def create_socket(db: Session, stu_id: str, socket_id: str):
    db_socket = models.Socket(stu_id=stu_id, socket_id=socket_id)
    db.add(db_socket)
    db.commit()
    db.refresh(db_socket)
    return db_socket

def update_socket(db: Session, stu_id: str, socket_id: str):
    db_socket = get_socket_by_stuid(db=db, stu_id=stu_id)
    db_socket.socket_id = socket_id
    db.commit()
    db.refresh(db_socket)
    return db_socket

#######################################################################################################################
#################################################### SOCKET ###########################################################
#######################################################################################################################