import pytest
from sqlalchemy import inspect
from datetime import date

from app import db, models, schemas
from app.crud import vehicles, maintenance


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_maintenance_create_list():
    inspector = inspect(db.engine)
    assert inspector.has_table("maintenance")

    session = db.SessionLocal()
    try:
        vehicle = vehicles.create_vehicle(
            session,
            schemas.VehicleCreate(plate="ABC123", model="Ford", year=2020),
        )
        maintenance.create_maintenance(
            session,
            schemas.MaintenanceCreate(
                vehicle_id=vehicle.id,
                kind="oil",
                due_date=date(2024, 1, 1),
            ),
        )
        records = maintenance.list_maintenance(session, vehicle_id=vehicle.id)
        assert len(records) == 1
        assert records[0].kind == "oil"
    finally:
        session.close()
