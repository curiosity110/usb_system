from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from .db import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    dob = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="client")


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    bookings = relationship("Booking", back_populates="trip")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    client = relationship("Client", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")

    __table_args__ = (UniqueConstraint("client_id", "trip_id", name="uix_client_trip"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    model = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SyncOutbox(Base):
    __tablename__ = "sync_outbox"
    id = Column(Integer, primary_key=True)
    model = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    logical_clock = Column(Integer, nullable=False, index=True)
    tombstone = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
