from sqlalchemy import Column, Integer, Text
from . import Base


class FAQ(Base):
    __tablename__ = 'faq'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
