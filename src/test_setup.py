from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base

# in-memory SQLite DB (temporary)
TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DB_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine)

# Initialize tables
def init_test_db():
    Base.metadata.create_all(bind=engine)
    print("Test DB initialized.")

