"""add sessions, logs, subscriptions tables — UUID PKs + FKs

Revision ID: a1b2c3d4e5f6
Revises: 🔴 YOUR_USERS_TABLE_REVISION
Create Date: 2026-09-28 00:14:34 UTC+7

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import func

# revision identifiers — UPDATE down_revision TO YOUR USERS MIGRATION!
revision = 'a1b2c3d4e5f6'
down_revision = '<<replace_with_users_migration_id>>'  # ⚠️ CRITICAL — update this!
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------
    # subscriptions table
    # ------------------------------
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_subscription_id', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum(
            'trialing', 'active', 'past_due', 'canceled', 'incomplete',
            'incomplete_expired', 'unpaid', 'paused',
            name='subscription_status'
        ), nullable=False, server_default='trialing'),
        sa.Column('plan_id', sa.String(length=100), nullable=False),
        sa.Column('plan_name', sa.String(length=255), nullable=True),
        sa.Column('interval', sa.String(length=20), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True, server_default='THB'),
        sa.Column('trial_start_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_start_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB().with_variant(sa.JSON(), 'sqlite', 'mysql'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(),
                  onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_subscription_id', name='uq_sub_provider_id'),
        # Foreign Key to users table
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            ondelete='CASCADE'
        ),
    )
    op.create_index('ix_subscriptions_user_active', 'subscriptions',
                    ['user_id', 'status'],
                    postgresql_where=sa.text("status NOT IN ('canceled', 'unpaid', 'incomplete_expired')"))

    # ------------------------------
    # sessions table
    # ------------------------------
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_token', sa.String(length=512), nullable=False, unique=True, index=True),
        sa.Column('refresh_token', sa.String(length=512), nullable=True, unique=True, index=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(),
                  onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        # Foreign Key to users table
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            ondelete='CASCADE'
        ),
    )
    op.create_index(
        'ix_sessions_active', 'sessions', ['user_id', 'expires_at'],
        postgresql_where=sa.text("revoked_at IS NULL AND expires_at > NOW()")
    )

    # ------------------------------
    # logs table
    # ------------------------------
    op.create_table(
        'logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=func.gen_random_uuid()),
        sa.Column('level', sa.Enum(
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
            name='log_level'
        ), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('trace_id', sa.String(length=128), nullable=True, index=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('module', sa.String(length=255), nullable=True),
        sa.Column('metadata', postgresql.JSONB().with_variant(sa.JSON(), 'sqlite', 'mysql'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.PrimaryKeyConstraint('id'),
        # Foreign Key to users table — SET NULL on user deletion
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            ondelete='SET NULL'
        ),
    )
    op.create_index('ix_logs_level_created', 'logs', ['level', 'created_at'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_logs_level_created', table_name='logs')
    op.drop_index('ix_sessions_active', table_name='sessions')
    op.drop_index('ix_subscriptions_user_active', table_name='subscriptions')

    # Drop tables (FK order matters — children first)
    op.drop_table('logs')
    op.drop_table('sessions')
    op.drop_table('subscriptions')

    # Drop enums (PostgreSQL only)
    op.execute('DROP TYPE IF EXISTS subscription_status;')
    op.execute('DROP TYPE IF EXISTS log_level;')
