from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# If the URL starts with postgresql://, translate it to postgresql+psycopg://
# to explicitly use the psycopg (v3) driver installed in our dependencies.
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args={"prepare_threshold": None}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency generator to get a database session and ensure clean closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
