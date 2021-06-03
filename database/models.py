import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime,
    Boolean,
)

Base = declarative_base()

# должны быть без id, иначе в один пост сможет войти несколько одинаковых тегов и наоборот
post_tag = Table('post_tag', Base.metadata,
                 # Column('id', Integer, primary_key=True),
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id')),
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref='posts')  # это не колонка !!!!! физически в базе этого не будет
    tags = relationship('Tag', secondary=post_tag, backref='posts')


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(250), nullable=False, unique=False)
    gb_id = Column(Integer, nullable=True, unique=True)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(2048), nullable=False, unique=False)
    # posts = relationship('Post', secondary='post_tag', backref='tags') # не нужно, тк есть secondary в Post


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref='comments')
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship(Post, backref='comments')

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.created_at = datetime.datetime.fromisoformat(kwargs["created_at"])
        self.hidden = kwargs["hidden"]
        self.deep = kwargs["deep"]
        self.time_now = datetime.datetime.fromisoformat(kwargs["time_now"])



