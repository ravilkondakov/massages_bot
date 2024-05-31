from sqlalchemy import Column, Integer, DateTime, ForeignKey
from . import Base


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    massage_id = Column(Integer, ForeignKey('massages.id'))
    appointment_time = Column(DateTime)
