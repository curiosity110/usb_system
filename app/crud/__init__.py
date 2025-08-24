"""CRUD package exporting resource modules."""
from . import bookings, clients, trips, vehicles, maintenance, reminders

__all__ = ["bookings", "clients", "trips", "vehicles", "maintenance", "reminders"]
