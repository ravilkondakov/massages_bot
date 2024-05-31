from sqlalchemy import Column, Integer, String, Boolean
from . import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    is_registered = Column(Boolean, default=False)

    @classmethod
    def register(cls, session, telegram_id, username):
        user = session.query(cls).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = cls(telegram_id=telegram_id, username=username, is_registered=True)
            session.add(user)
            session.commit()
            return user
        else:
            user.is_registered = True
            session.commit()
            return user
