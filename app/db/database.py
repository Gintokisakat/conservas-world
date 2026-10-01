import logging
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DB_URL

logger = logging.getLogger("conservas.db")

# Connection pooling para producción
_connect_args: dict[str, object] = {"check_same_thread": False}
_is_memory_sqlite = DB_URL.startswith("sqlite") and (
    ":memory:" in DB_URL or DB_URL.rstrip("/").endswith("sqlite:")
)
if DB_URL.startswith("sqlite"):
    # SQLite: usar WAL mode para mejor concurrencia
    _connect_args["timeout"] = 30

# Las bases SQLite en memoria usan SingletonThreadPool, que no admite
# dimensionamiento de pool; solo lo aplicamos donde tiene efecto.
_pool_kwargs: dict[str, object] = (
    {}
    if _is_memory_sqlite
    else {"pool_pre_ping": True, "pool_size": 5, "max_overflow": 10}
)

engine = create_engine(
    DB_URL,
    connect_args=_connect_args,
    **_pool_kwargs,  # type: ignore[arg-type]
)


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    if DB_URL.startswith("sqlite"):
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
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


def init_db(use_alembic: bool = True):
    """Deja el schema listo.

    Camino normal (roadmap 5.1): corre las migraciones de Alembic. Si la base
    ya tenía schema pero nunca se versionó (bases previas a Alembic), se
    marca como `head` en vez de re-intentar el baseline, que destruiría datos.

    `use_alembic=False` conserva el `create_all` original para tests y para
    entornos donde Alembic no esté disponible.
    """
    from app.db import models  # noqa: F401

    if not use_alembic:
        Base.metadata.create_all(bind=engine)
        _migrate()
        return

    try:
        _run_alembic_upgrade()
    except Exception:  # pragma: no cover - degradar a create_all
        logger.warning(
            "Alembic no disponible o falló; usando create_all", exc_info=True
        )
        Base.metadata.create_all(bind=engine)
        _migrate()
        return
    _migrate()


def _alembic_config():
    from alembic.config import Config

    root = Path(__file__).resolve().parents[2]
    ini = root / "alembic.ini"
    cfg = Config(str(ini)) if ini.is_file() else Config()
    cfg.set_main_option("script_location", str(root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", DB_URL)
    return cfg


def _has_version_table() -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        ).fetchone()
    return row is not None


def _has_any_table() -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version' LIMIT 1"
            )
        ).fetchone()
    return row is not None


def _run_alembic_upgrade() -> None:
    """Aplica `alembic upgrade head`, sellando antes las bases preexistentes."""
    from alembic import command

    cfg = _alembic_config()
    if not _has_version_table() and _has_any_table():
        # Base creada por create_all antes de adoptar Alembic: se marca como
        # head para que la app funcione y las migraciones futuras sí corran.
        logger.info("Base sin versionar; sellando en head")
        command.stamp(cfg, "head")
    command.upgrade(cfg, "head")


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
