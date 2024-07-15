from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func
from config.database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=True)
    text = Column(String, nullable=True)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
