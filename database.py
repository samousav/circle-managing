import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from pathlib import Path
import dotenv, time, uuid

dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "database.db"

engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")

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
    user_id = Column(Integer, ForeignKey("users.chat_id"), nullable=False)
    user = relationship("User", back_populates="circles")


class AppSession(Base):
    __tablename__ = "app_sessions"
    token = Column(String, primary_key=True)
    chat_id = Column(Integer, nullable=True)
    created_at = Column(Integer, )


class PendingVerification(Base):
    __tablename__ = "pending_verifications"
    code = Column(String, primary_key=True)
    session_token = Column(String, nullable=False)
    expires_at = Column(Integer, nullable=False)


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


def create_anonymous_session():
    new_token = str(uuid.uuid4())
    with Session() as session:
        new_session = AppSession(token=new_token, created_at=int(time.time()))
        session.add(new_session)
        session.commit()
    return new_token



def generate_pending_code_for_session(code: str):
    with Session() as session:
        current_time = int(time.time())
        session.query(PendingVerification).filter(PendingVerification.expires_at < current_time).delete()
        new_pending = PendingVerification(code=code, expires_at=current_time+120)
        session.add(new_pending)
        session.commit()


def link_chat_id_to_code(code: str, chat_id: int):
    with Session() as session:
        current_time = int(time.time())
        pending = session.query(PendingVerification).filter(
            PendingVerification.code == code,
            PendingVerification.expires_at > current_time,
            PendingVerification.chat_id == None,
        )

        if pending:
            pending.chat_id == chat_id
            session.commit()
            return True
        return False


def get_chat_id_by_session(session_token: str):
    if not session_token:
        return None
    with Session() as session:
        app_session = session.query(AppSession).filter(AppSession.token == session_token).first()
        if app_session and app_session.chat_id:
            return app_session.chat_id
    return None

def link_tma_to_session(session_token: str, chat_id: int):
    with Session() as session:
        app_session = session.query(AppSession).filter(AppSession.token == session_token).first()
        if app_session:
            app_session.chat_id = chat_id
            session.commit()

def logout_all_devices(chat_id: int):
    with Session() as session:
        session.query(AppSession).filter(AppSession.chat_id == chat_id).delete()
        session.commit()

        




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

        friend_to_delete = (
            session.query(Circle)
            .filter(
                Circle.user_id == user.chat_id,
                func.trim(Circle.fullname).ilike(fullname.strip()),
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
            session.query(Circle)
            .filter(
                Circle.user_id == user.chat_id,
                func.trim(Circle.fullname).ilike(fullname.strip()),
            )
            .first()
        )

        if friend_to_update:
            setattr(friend_to_update, field, value)
            session.commit()
            return True
        return False


# ======================== ADMIN ACTIONS ========================


def get_all_users():
    with Session() as session:
        result = (
            session.query(User, func.count(Circle.id).label("friend_count"))
            .outerjoin(Circle, User.chat_id == Circle.user_id)
            .group_by(User.id)
            .all()
        )
        return [
            {
                "id": row.User.id,
                "chat_id": row.User.chat_id,
                "name": row.User.name,
                "username": row.User.username,
                "language": row.User.language,
                "friend_count": row.friend_count,
            } for row in result
        ]
