from sqlalchemy import Column, Integer, String, Text
from . import Base


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    description = Column(Text)
