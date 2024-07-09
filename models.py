from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class FormData(Base):
    __tablename__ = "form"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bike = Column(String, nullable=True)
    boots = Column(String, nullable=True)
    insoles = Column(String, nullable=True)
    pedals = Column(String, nullable=True)
    other_bikes = Column(String, nullable=True)
    tool_annotation = Column(String, nullable=True)
    sport_history = Column(String, nullable=True)
    sport_annotation = Column(String, nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    message = relationship("Message", backref="form", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    form = relationship("FormData", backref="client", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=True)
    text = Column(String, nullable=True)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
