import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey

# Shared MetaData instance
metadata = MetaData()

# Users Table (SQLAlchemy Core)
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(255), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("name", String(255), nullable=True),
    Column("created_at", DateTime, default=datetime.datetime.utcnow)
)

# Todos Table (SQLAlchemy Core)
todos_table = Table(
    "todos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("parent_todo_id", Integer, ForeignKey("todos.id"), nullable=True),
    Column("month", String(50), nullable=False, default="July"),
    Column("day", String(10), nullable=False, default="30"),
    Column("completed", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow)
)
