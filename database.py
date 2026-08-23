from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL


# =========================================================
# DATABASE ENGINE
# =========================================================

# For PostgreSQL on a live server, drop idle connections automatically and
# verify connections before use (important for cloud Postgres / serverless).
connect_args = {}

if DATABASE_URL.startswith("postgresql"):
    connect_args = {"connect_args": {"sslmode": "require"}}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    **connect_args
)


# =========================================================
# BASE
# =========================================================

Base = declarative_base()


# =========================================================
# SESSION
# =========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


# =========================================================
# GET DATABASE SESSION
# =========================================================

def get_db():

    return SessionLocal()


# =========================================================
# CREATE TABLES
# =========================================================

def init_db():

    from models import User, Payment

    Base.metadata.create_all(
        bind=engine
    )