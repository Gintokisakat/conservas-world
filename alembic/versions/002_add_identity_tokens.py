"""add identity verification/reset fields to users

Revision ID: 002_identity
Revises: 001_tsvector
Create Date: 2026-10-03 23:30:00
"""
import sqlalchemy as sa
from alembic import op

revision = '002_identity'
down_revision = '001_tsvector'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('email_verification_token_hash', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_reset_token_hash', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_reset_used_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'password_reset_used_at')
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token_hash')
    op.drop_column('users', 'email_verification_expires_at')
    op.drop_column('users', 'email_verification_token_hash')
    op.drop_column('users', 'email_verified_at')
