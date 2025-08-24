import pytest
from sqlalchemy import inspect

from app import db, models, schemas
from app.crud import vehicles


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_vehicle_create_list():
    inspector = inspect(db.engine)
    assert inspector.has_table("vehicles")

    session = db.SessionLocal()
    try:
        vehicles.create_vehicle(
            session,
            schemas.VehicleCreate(plate="ABC123", model="Ford", year=2020, notes="A"),
        )
        vehicles.create_vehicle(
            session,
            schemas.VehicleCreate(plate="XYZ789", model="Toyota", year=2021),
        )
        all_vehicles = vehicles.list_vehicles(session)
        assert len(all_vehicles) == 2
        plates = {v.plate for v in all_vehicles}
        assert {"ABC123", "XYZ789"} == plates
    finally:
        session.close()
