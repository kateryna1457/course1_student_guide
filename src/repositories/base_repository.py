from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class BaseRepository(ABC):
    """
    Абстрактний базовий клас для репозиторіїв.

    Визначає інтерфейс для CRUD операцій.
    """

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Створити новий запис.

        Args:
            data: Словник з даними для створення

        Returns:
            Optional[int]: ID створеного запису або None
        """
        pass

    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Отримати запис за ID.

        Args:
            record_id: ID запису

        Returns:
            Optional[Dict[str, Any]]: Словник з даними або None
        """
        pass

    @abstractmethod
    def get_all(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Отримати всі записи з пагінацією.

        Args:
            offset: Зміщення
            limit: Кількість записів

        Returns:
            List[Dict[str, Any]]: Список записів
        """
        pass

    @abstractmethod
    def search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Пошук записів за критеріями.

        Args:
            params: Параметри пошуку

        Returns:
            List[Dict[str, Any]]: Список знайдених записів
        """
        pass

    @abstractmethod
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Оновити запис.

        Args:
            record_id: ID запису
            data: Дані для оновлення

        Returns:
            bool: True якщо оновлення успішне
        """
        pass

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """
        Видалити запис.

        Args:
            record_id: ID запису

        Returns:
            bool: True якщо видалення успішне
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Порахувати кількість записів.

        Returns:
            int: Загальна кількість записів
        """
        pass

    @abstractmethod
    def exists(self, record_id: int) -> bool:
        """
        Перевірити чи існує запис.

        Args:
            record_id: ID запису

        Returns:
            bool: True якщо запис існує
        """
        pass
