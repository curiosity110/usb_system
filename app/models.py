"""SQLAlchemy models."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for declarative models."""
    pass


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True)
    normalized_phone = Column(String, nullable=True, unique=True, index=True)

    bookings = relationship("Booking", back_populates="client")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="trip")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)

    client = relationship("Client", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")

    __table_args__ = (UniqueConstraint("client_id", "trip_id", name="uq_booking_client_trip"),)
