"""SQLAlchemy models."""
from __future__ import annotations

import uuid

from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for declarative models."""
    pass


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    email = Column(String, nullable=True, unique=True, index=True)  # <= allow NULL if you want
    phone = Column(String, nullable=True)
    normalized_phone = Column(String, nullable=True, unique=True, index=True)  # <= keep as Column
    dob = Column(Date, nullable=True)

    bookings = relationship("Booking", back_populates="client")

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    # IMPORTANT: do NOT also define @property normalized_phone here.
    # If you want a computed helper, name it something else, e.g.:
    # def normalized_phone_computed(self): ...
    
    
class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # ADD THESE:
    destination = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    notes = Column(String(1000), nullable=True)

    bookings = relationship("Booking", back_populates="trip")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)

    client = relationship("Client", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")

    __table_args__ = (UniqueConstraint("client_id", "trip_id", name="uq_booking_client_trip"),)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditLog(Base):
    """Simple audit log table capturing entity changes."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)


class SyncOutbox(Base):
    """Outbox table for synchronization."""

    __tablename__ = "sync_outbox"

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    logical_clock = Column(Integer, nullable=False)
    op = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("entity", "entity_id", "logical_clock", name="uq_sync_clock"),
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    plate = Column(String, nullable=False, unique=True, index=True)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    maintenance_records = relationship("Maintenance", back_populates="vehicle")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    vehicle = relationship("Vehicle", back_populates="maintenance_records")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    scope = Column(String, nullable=False)
    ref_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    assigned_role = Column(String, nullable=True)
    done_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("scope IN ('global','vehicle','trip','client')", name="ck_reminder_scope"),
    )
