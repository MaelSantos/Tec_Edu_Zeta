from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.utils.constants import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

session = SessionLocal()

def get_db():
    with SessionLocal() as db:
        yield db
