from sqlalchemy import Column, Integer, String
from . import Base


class Massage(Base):
    __tablename__ = 'massages'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
