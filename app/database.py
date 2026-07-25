from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import Config

settings = Config()
engine = create_engine(str(settings.database_url), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
