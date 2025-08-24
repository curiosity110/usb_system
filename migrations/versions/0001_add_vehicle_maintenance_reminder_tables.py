from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("plate", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("plate"),
    )

    op.create_table(
        "maintenance",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("vehicle_id", sa.String(), sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "reminders",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("ref_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("assigned_role", sa.String(), nullable=True),
        sa.Column("done_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("scope IN ('global','vehicle','trip','client')", name="ck_reminder_scope"),
    )


def downgrade() -> None:
    op.drop_table("reminders")
    op.drop_table("maintenance")
    op.drop_table("vehicles")
