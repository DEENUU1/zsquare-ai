from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func, Boolean
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
    position_problem = Column(String, nullable=True)
    adnotation_position_problem = Column(String, nullable=True)
    years_cycling = Column(Integer, nullable=True)
    annual_mileage = Column(Integer, nullable=True)
    weekly_rides = Column(Integer, nullable=True)
    session_duration = Column(String, nullable=True)
    participated_in_races = Column(Boolean, nullable=True)
    best_results = Column(String, nullable=True)
    intensity_measurement = Column(String, nullable=True)
    other_sports = Column(String, nullable=True)
    bike_confidence = Column(Integer, nullable=True)
    gear_changing = Column(Boolean, nullable=True)
    autumn_winter_riding = Column(Boolean, nullable=True)
    preferred_grip = Column(String, nullable=True)
    cadence_comfort = Column(String, nullable=True)
    group_riding_skills = Column(String, nullable=True)
    cornering_style = Column(String, nullable=True)
    brake_usage = Column(String, nullable=True)
    tire_pressure_check = Column(String, nullable=True)
    injuries = Column(String, nullable=True)
    injuries_during_cycling = Column(Boolean, nullable=True)
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
