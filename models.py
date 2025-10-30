from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AppointmentRecord(Base):
    __tablename__ = "appointment_records"

    record_id = Column(String, primary_key=True)
    access_code = Column(String, index=True, unique=True, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    expiration_time = Column(DateTime(timezone=True), nullable=False)
    service_id = Column(String, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

class EventRegistration(Base):
    __tablename__ = "event_registrations"

    record_id = Column(String, primary_key=True)
    access_code = Column(String, index=True, unique=True, nullable=False)
    event_name = Column(String, nullable=False)
    expiration_time = Column(DateTime(timezone=True), nullable=False)