from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from datetime import datetime, date

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    user_name: Mapped[str] = mapped_column(String(40), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(40), nullable=True)
    created_at: Mapped["datetime"] = mapped_column(DateTime, default=datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")

    following:Mapped[list["Followers"]] = relationship(back_populates="follower",foreign_keys="Followers.followed_id")
    followers:Mapped[list["Followers"]] = relationship(back_populates="followed",foreign_keys="Followers.follower_id")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_name": self.user_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "total_posts": len(self.posts),
            "total_comments": len(self.comments),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Post(db.Model):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship("User", back_populates = "posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    medias: Mapped[list["Media"]] = relationship("Media", back_populates = "post")

    def serialize(self):
        return {
            "id": self.id,
            "user": {
                "user_name": self.user.user_name
            } if self.user else None
        }
    
class Comment(db.Model):
    __tablename__ = 'comment'
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(Text(), nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))

    user: Mapped["User"] = relationship("User", back_populates= "comments", uselist=False)
    post: Mapped["Post"] = relationship("Post", back_populates= "comments", uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": {
                "id": self.user.id,
                "user_name": self.user.user_name
            } if self.user else None
        }
class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"

class Media(db.Model):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))

    post: Mapped["Post"] = relationship("Post", back_populates="medias", uselist=False)

    def serialize(self):
        return {
            "url_media": self.url,
            "type": self.type.value,
            "post_author": {
                "id": self.post.user.id,
                "user_name": self.post.user.user_name
            } if self.post and self.post.user else None
        }   
    
class Followers(db.Model):
    __tablename__ = 'followers'
    id: Mapped[int] = mapped_column(primary_key=True)

    follower_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    followed_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    follower: Mapped["User"] = relationship(back_populates="following", foreign_keys=[follower_id])
    followed: Mapped["User"] = relationship(back_populates="followers", foreign_keys=[followed_id])

    def serialize(self):
        return {
            "id": self.id,
            "user": {
                "id": self.user.id,
                "email": self.user.email
            } if self.user else None,
        }

    