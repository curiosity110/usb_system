import pytest
from sqlalchemy import inspect
from datetime import date

from app import db, models, schemas
from app.crud import reminders


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_reminder_create_list():
    inspector = inspect(db.engine)
    assert inspector.has_table("reminders")

    session = db.SessionLocal()
    try:
        reminders.create_reminder(
            session,
            schemas.ReminderCreate(
                scope="global",
                title="Check",
                due_date=date(2024, 1, 1),
                assigned_role="admin",
            ),
        )
        all_reminders = reminders.list_reminders(session)
        assert len(all_reminders) == 1
        assert all_reminders[0].scope == "global"
    finally:
        session.close()
