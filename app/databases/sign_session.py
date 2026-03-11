from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SIGN_DATABASE_URL = (
    f"mysql+pymysql://{settings.SIGN_DB_USER}:{settings.SIGN_DB_PASSWORD}"
    f"@{settings.SIGN_DB_HOST}:{settings.SIGN_DB_PORT}/{settings.SIGN_DB_NAME}"
)

sign_engine = create_engine(SIGN_DATABASE_URL)
SignSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sign_engine)

SignBase = declarative_base()


def get_sign_db():
    db = SignSessionLocal()
    try:
        yield db
    finally:
        db.close()
