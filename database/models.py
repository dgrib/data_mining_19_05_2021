from sqlalchemy.ext.declarative import declarative_base
# функция declarative_base возвращает класс от которого мы д наследовать все кдассы моделей, относящиеся к одной бд
# это связующее звено между наштими таюблицами

# для убодства действий с foreign key , а напрямую у нас етсь только id
# когда forKey ссылается на какойто объект другой таблицы атрибут relationship он знает об этом и сам сделает запрос.
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,  # эти типы используются не питоновские и их надо декларировать,
    # использовать типы которые поедоставляет ORM библиотека,
    # используем слой абстракции чтобы пистаь одно а в разные типы бд ходить sqlite postgres и тд,
    # будет знать как обращяться к этим объектам чтобы это было корректно
    String,
    ForeignKey,
    Table
)

# опишем базовую структуру поста , что она имеет

# Base это связукющее звено нескольких классов, в базе же может быть несколько таблиц, и Post и тд принадлежат одной бд
Base = declarative_base()


class Post(Base):
    __tablename__ = 'post'  # предпочитает указывать явно , но если не указщывать то по имени клааса присваивается само
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    # id поста берем с сайта, поэтому не автоинкримент
    url = Column(String(2048), nullable=False, unique=True)
    # абстракция String выберет сама тот тип которы будет подходить определенную бд
    # без url запись не м существовать поэтому nullable False
    # можем указать ограничения сми, так как url не мб больше 2048 символов
    title = Column(String, nullable=True, unique=False)
    # длина неизвестная - ограничения не вешаем
    # записи мб с одинаковыми title поэтому unique=False
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    # так как relationship то тип колонки дб как у того на что ссылается, то есть инт, как id у Author класса
    # указывает по __tablename__ = author, и появляется физическая связь с типом интежер
    # не могу создать пост без автора nullable=False

    # но когда я получу экземпляр класса Post у меня не будет экземпляра класса Author а будет интежер,
    # но я хочу, имея на руках экземпляр Post, обратиться к атрибуту и по нему получить не интежер Author,
    # а получить экземпляр класса Author
    author = relationship("Author", backref='posts')  # это не колонка !!!!! физически в базе этого не будет
    # нужно указать класс Author Но питон его не видит ьтак как создан Автор после,
    # томожеим указать в виде строки имя класса
    # backref='posts' означает что у экземплчяра класса Автор появится атрибут posts,
    # обращение к которому будет отдавать список экземпляров класса Post, которые связаны с этим автором
    # можно было в Автор сделать relationship, но зачем если можно backref сделать - обратная связь
    tags = relationship('Tag', secondary='post_tag', backref='posts')


class Author(Base):  # будем хранить автора
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # будем сами задавать индекс
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(250), nullable=False, unique=False)
    # записи мб с одинаковыми title поэтому unique=False


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(2048), nullable=False, unique=False)  # пусть будет как Author, уникальный только url
    posts = relationship('Post', secondary='post_tag', backref='tags')


# должны быть без id, иначе в один пост сможет войти несколько одинаковых тегов
PostTag = Table('post_tag', Base.metadata,
                # Column('id', Integer, primary_key=True),
                Column('post_id', Integer, ForeignKey('Post.id')),
                Column('tag_id', Integer, ForeignKey('Tag.id')),
                )


# association_table = Table('association',
#     Column('left_id', Integer, ForeignKey('left.id')),
#     Column('right_id', Integer, ForeignKey('right.id'))
# )
# class Parent(Base):
#     __tablename__ = 'left'
#     id = Column(Integer, primary_key=True)
#     children = relationship("Child", secondary=association_table, back_populates="parents")
#
# class Child(Base):
#     __tablename__ = 'right'
#     id = Column(Integer, primary_key=True)
#     parents = relationship("Parent", secondary=association_table, back_populates="children")



