"""add tsvector to products for FTS

Revision ID: 001_tsvector
Revises: bc8b230c4d88
Create Date: 2026-10-03 20:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_tsvector'
down_revision = 'bc8b230c4d88'
branch_labels = None
depends_on = None


def upgrade():
    # Añadir columna tsvector
    op.add_column('products', sa.Column('tsv', sa.Text(), nullable=True))

    # Crear índice GIN sobre tsvector (usando to_tsvector). SQLite no soporta, pero Alembic es genérico;
    # para Postgres se usa USING GIN y función. Usamos batch_op si necesario, pero directo.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_products_tsv 
        ON products USING GIN (to_tsvector('simple', coalesce(name,'')))
        """
    )


def downgrade():
    op.drop_index('idx_products_tsv', table_name='products')
    op.drop_column('products', 'tsv')
