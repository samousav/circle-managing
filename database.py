import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
import os
import dotenv

dotenv.load_dotenv()

engine = sqlalchemy.create_engine(f"sqlite:///database.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    name = Column(String)
    username = Column(String)
    language = Column(String, default="fa", server_default="fa")
    circles = relationship("Circle", back_populates="user")


class Circle(Base):
    __tablename__ = "circles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    nickname = Column(String)
    birthday = Column(String)
    phone = Column(String)
    location = Column(String)

    # Note: Points to chat_id, meaning user_id stores the Telegram ID
    user_id = Column(Integer, ForeignKey("users.chat_id"), nullable=False)
    user = relationship("User", back_populates="circles")


# ======================== DATABASE ACTIONS ========================

def create_tables():
    Base.metadata.create_all(engine)


def create_user(chat_id, name, username, language="fa"):
    with Session() as session:
        user = User(chat_id=chat_id, name=name, username=username, language=language)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user(chat_id):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        return user


# ======================== USER ACTIONS ========================

def set_user_language(chat_id, language):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user:
            user.language = language
            session.commit()
            return True
        return False


def get_user_language(chat_id):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user and user.language:
            return user.language
        return "fa"

def add_friend_to_db(chat_id, fullname, nickname, birthday, phone, location):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            return False

        new_friend = Circle(
            fullname=fullname,
            nickname=nickname,
            birthday=birthday,
            phone=phone,
            location=location,
            user=user,
        )
        session.add(new_friend)
        session.commit()
        return True


def get_friends_from_db(chat_id):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user or not user.circles:
            return False

        friends = []
        for friend in user.circles:
            friends.append(
                {
                    "fullname": friend.fullname,
                    "nickname": friend.nickname,
                    "birthday": friend.birthday,
                    "phone": friend.phone,
                    "location": friend.location,
                }
            )
        return friends


def remove_friend_from_db(chat_id, fullname):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            return False

        # FIX: Compared user_id to user.chat_id, and used trim/ilike to prevent spacing/casing bugs
        friend_to_delete = (
            session.query(Circle)
            .filter(
                Circle.user_id == user.chat_id, 
                func.trim(Circle.fullname).ilike(fullname.strip())
            )
            .first()
        )
        
        if friend_to_delete:
            session.delete(friend_to_delete)
            session.commit()
            return True
        return False
    


def update_friend_info(chat_id, fullname, field, value):
    with Session() as session:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            return False
        
        friend_to_update = (
            session.query(Circle).filter(Circle.user_id == user.chat_id, func.trim(Circle.fullname).ilike(fullname.strip())).first()
        )

        if friend_to_update:
            setattr(friend_to_update, field, value)
            session.commit()
            return True
        return False
    