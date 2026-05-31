"""
Модуль репозиторіїв (Repository Pattern).

Експортує репозиторії для роботи з даними.
"""

from .base_repository import BaseRepository
from .database import DatabaseConnection, get_db
from .postgres_repository import StudentRepository
from .export_repository import ExportRepository

__all__ = [
    "BaseRepository",
    "DatabaseConnection",
    "get_db",
    "StudentRepository",
    "ExportRepository"
]
