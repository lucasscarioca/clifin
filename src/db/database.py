import sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Generator

# Database configuration
DB_NAME = "clifin.db"
DB_PATH = Path(__file__).parent.parent.parent / DB_NAME


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections.

    Ensures connections are properly closed and provides
    row factory for dict-like access.

    Yields:
        sqlite3.Connection: Database connection

    Example:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    finally:
        if conn:
            conn.close()


def init_db() -> None:
    """Initialize database by running Alembic migrations.

    This ensures the database file exists and runs any pending migrations.
    Use: uv run alembic upgrade head

    Raises:
        RuntimeError: If database initialization fails
    """
    # Just ensure the database file exists
    # Migrations are now handled by Alembic
    DB_PATH.touch(exist_ok=True)
