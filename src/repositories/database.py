"""
Database connection manager.

Управління підключеннями до PostgreSQL через psycopg2.
"""

import logging
import psycopg2
from psycopg2 import pool, Error as PostgresError
from psycopg2.extras import RealDictCursor
from typing import Optional
from contextlib import contextmanager

from src.config import get_database_url, get_database_schema
from src.constants import DB_POOL_MIN_CONNECTIONS, DB_POOL_MAX_CONNECTIONS

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Менеджер підключень до бази даних.

    Використовує connection pool для ефективного управління з'єднаннями.
    """

    _instance: Optional['DatabaseConnection'] = None
    _pool: Optional[pool.SimpleConnectionPool] = None

    def __new__(cls):
        """Singleton pattern - один екземпляр на додаток."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Ініціалізація connection pool."""
        # Don't initialize pool immediately - do it lazily on first use
        pass

    def _initialize_pool(self):
        """Створити connection pool."""
        try:
            database_url = get_database_url()
            self._pool = pool.SimpleConnectionPool(
                minconn=DB_POOL_MIN_CONNECTIONS,
                maxconn=DB_POOL_MAX_CONNECTIONS,
                dsn=database_url
            )
            logger.info("Database connection pool created successfully")
        except PostgresError as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise

    def _ensure_pool(self):
        """Ensure connection pool is initialized (lazy initialization)."""
        if self._pool is None:
            self._initialize_pool()

    @contextmanager
    def get_connection(self):
        """
        Context manager для отримання з'єднання з pool.

        Yields:
            connection: PostgreSQL connection

        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # ... use connection
        """
        self._ensure_pool()  # Lazy init
        conn = None
        try:
            conn = self._pool.getconn()
            # Set search path to schema
            with conn.cursor() as cur:
                schema = get_database_schema()
                cur.execute(f"SET search_path TO {schema}, public;")
            yield conn
            conn.commit()
        except PostgresError as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Context manager для отримання cursor.

        Args:
            cursor_factory: Тип cursor (за замовчуванням RealDictCursor)

        Yields:
            cursor: Database cursor

        Example:
            with db.get_cursor() as cur:
                cur.execute("SELECT * FROM t_students")
                results = cur.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(self, query: str, params: tuple = None):
        """
        Виконати SELECT запит та отримати результати.

        Args:
            query: SQL запит
            params: Параметри запиту

        Returns:
            List[dict]: Список результатів як словників
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute_one(self, query: str, params: tuple = None):
        """
        Виконати SELECT запит та отримати один результат.

        Args:
            query: SQL запит
            params: Параметри запиту

        Returns:
            Optional[dict]: Один результат як словник або None
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """
        Виконати INSERT запит та отримати ID.

        Args:
            query: SQL запит (має включати RETURNING id)
            params: Параметри запиту

        Returns:
            Optional[int]: ID нового запису або None
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result['id'] if result else None

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Виконати UPDATE/DELETE запит.

        Args:
            query: SQL запит
            params: Параметри запиту

        Returns:
            int: Кількість оброблених рядків
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount

    def close(self):
        """Закрити connection pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")

    def test_connection(self) -> bool:
        """
        Перевірити підключення до бази даних.

        Returns:
            bool: True якщо підключення успішне
        """
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                return result is not None
        except PostgresError as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Глобальний екземпляр (singleton)
db = DatabaseConnection()


# Convenience functions
def get_db() -> DatabaseConnection:
    """
    Отримати екземпляр DatabaseConnection.

    Returns:
        DatabaseConnection: Singleton екземпляр
    """
    return db
