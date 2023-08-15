from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    stu_id = Column(String, primary_key=True, index=True)
    password = Column(String)
    user_name = Column(String)
    name = Column(String)
    sex = Column(Integer)
    faculty = Column(String)
    stu_id_perm = Column(Integer)
    user_name_perm = Column(Integer)
    name_perm = Column(Integer)
    sex_perm = Column(Integer)
    follower_perm = Column(Integer)
    following_perm = Column(Integer)

class Follow(Base):
    __tablename__ = "followers"

    id = Column(Integer, primary_key=True, index=True)
    followed = Column(String)
    follower = Column(String)

class Block(Base):
    __tablename__ = "blocklist"

    id = Column(Integer, primary_key=True, index=True)
    blocker = Column(String)
    blocked = Column(String)

class UserAddInfo(Base):
    __tablename__ = "usersaddinfo"

    stu_id = Column(String, primary_key=True, index=True)
    birth_date = Column(String)
    status = Column(String)
    major = Column(String)
    year = Column(Integer)
    interest = Column(String)
    label = Column(String)
    avatar = Column(String)
    phone = Column(String)
    birth_date_perm = Column(Integer)
    status_perm = Column(Integer)
    major_perm = Column(Integer)
    year_perm = Column(Integer)
    interest_perm = Column(Integer)
    label_perm = Column(Integer)
    avatar_perm = Column(Integer)
    phone_perm = Column(Integer)

class Memory(Base):
    __tablename__ = "memories"

    post_id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    time = Column(String)
    photo_list = Column(String)
    like_list = Column(String)
    comment_list = Column(String)
    repo_list = Column(String)
    stu_id = Column(String)
    pms = Column(Integer)
    is_anonymous = Column(Integer)

class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    stu_id = Column(String)
    time = Column(String)
    content = Column(String)
    photo_list = Column(String)
    pms = Column(Integer)
    is_anonymous = Column(Integer)
    is_posted = Column(Integer)

class Photo(Base):
    __tablename__ = "photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    address = Column(String)

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    stu_id = Column(String)
    post_id = Column(Integer)
    time = Column(String)
    like_list = Column(String)
    content = Column(String)


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)


class LikeNotice(Base):
    __tablename__ = "likenotice"

    id = Column(Integer, primary_key=True, index=True)
    from_stu_id = Column(String)
    to_stu_id = Column(String)
    read = Column(Integer)
    post_id = Column(Integer)
    comment_id = Column(Integer)
    time = Column(String)


class CommentNotice(Base):
    __tablename__ = "commentnotice"

    id = Column(Integer, primary_key=True, index=True)
    from_stu_id = Column(String)
    to_stu_id = Column(String)
    comment_id = Column(Integer)
    time = Column(String)
    read = Column(Integer)


class RepoNotice(Base):
    __tablename__ = "reponotice"

    id = Column(Integer, primary_key=True, index=True)
    from_stu_id = Column(String)
    to_stu_id = Column(String)
    post_id = Column(Integer)
    time = Column(String)
    read = Column(Integer)


class FollowNotice(Base):
    __tablename__ = "follownotice"

    id = Column(Integer, primary_key=True, index=True)
    from_stu_id = Column(String)
    to_stu_id = Column(String)
    time = Column(String)
    read = Column(Integer)


class SystemNotice(Base):
    __tablename__ = "systemnotice"

    id = Column(Integer, primary_key=True, index=True)
    stu_id = Column(String)
    content = Column(String)
    title = Column(String)
    read = Column(Integer)
    time = Column(String)
    admin_id = Column(Integer)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(String)
    to_id = Column(String)
    text = Column(String)
    image = Column(String)
    time = Column(String)
    is_read = Column(Integer)
    is_sender_delete = Column(Integer)
    is_receiver_delete = Column(Integer)
    is_recall = Column(Integer)
    
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(String)
    password = Column(String)
    cover_url = Column(String)
    video_url = Column(String)
    name = Column(String)
    description = Column(String)
    pms = Column(Integer)
    user_list = Column(String)
    message_list = Column(String)
    video_pos_millis = Column(Integer)
    video_play = Column(Integer)
    video_cur_time = Column(String)

class Wait(Base):
    __tablename__ = "waitings"

    stu_id = Column(Integer, primary_key=True, index=True)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    id0 = Column(String)
    id1 = Column(String)
    time = Column(String)
    is_end = Column(Integer)

class RoomMessageRec(Base):
    __tablename__ = "roomMessageRec"

    id = Column(Integer, primary_key=True, index=True)
    stu_id = Column(String)
    room_id = Column(String)
    message_id = Column(Integer)

class Socket(Base):
    __tablename__ = "sockets"

    stu_id = Column(String, primary_key=True, index=True)
    socket_id = Column(String)