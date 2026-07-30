import os
from sqlalchemy import create_engine
from models import metadata, users_table, todos_table

# PostgreSQL Connection String (pgAdmin 4 - training_db)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:123456@localhost:5432/training_db"
)

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    try:
        metadata.create_all(engine)
    except Exception as e:
        print(f"Database initialization info: {e}")

if __name__ == "__main__":
    init_db()
    print("Database tables initialized in PostgreSQL (training_db) via models.py.")
