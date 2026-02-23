"""init core tables

Revision ID: 20260223_0001
Revises:
Create Date: 2026-02-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260223_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "prediction_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.String(length=64), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("features", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("predicted_value", sa.Numeric(12, 3), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_sku_created", "prediction_history", ["sku_id", "created_at"], unique=False)
    op.create_index("ix_prediction_user_created", "prediction_history", ["user_id", "created_at"], unique=False)
    op.create_index("ix_prediction_request_hash", "prediction_history", ["request_hash"], unique=False)
    op.create_index("ix_prediction_model_version", "prediction_history", ["model_version"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("actor_user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_action_created", "audit_logs", ["action", "created_at"], unique=False)
    op.create_index("ix_audit_actor_created", "audit_logs", ["actor_user_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_audit_actor_created", table_name="audit_logs")
    op.drop_index("ix_audit_action_created", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_prediction_model_version", table_name="prediction_history")
    op.drop_index("ix_prediction_request_hash", table_name="prediction_history")
    op.drop_index("ix_prediction_user_created", table_name="prediction_history")
    op.drop_index("ix_prediction_sku_created", table_name="prediction_history")
    op.drop_table("prediction_history")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
