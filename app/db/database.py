from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DB_URL

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    """ALTER TABLE idempotente para columnas añadidas tras crear la DB."""
    with engine.begin() as conn:
        has_image = conn.execute(
            text(
                "SELECT 1 FROM pragma_table_info('products') WHERE name = 'image_url'"
            )
        ).fetchone()
        if has_image is None:
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)"))
