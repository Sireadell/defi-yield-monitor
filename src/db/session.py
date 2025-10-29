from contextlib import contextmanager
from src.db.database import SessionLocal

@contextmanager
def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # rollback if any error occurs
        raise e
    finally:
        db.close()
