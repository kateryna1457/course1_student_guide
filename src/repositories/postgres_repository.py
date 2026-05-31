"""
PostgreSQL репозиторій для студентів.

Реалізація Repository Pattern для роботи з таблицею t_students.
"""

import logging
from typing import Optional, List, Dict, Any
from psycopg2 import Error as PostgresError

from .base_repository import BaseRepository
from .database import get_db

logger = logging.getLogger(__name__)


class StudentRepository(BaseRepository):
    """
    Репозиторій для роботи з студентами через PostgreSQL.

    Використовує прямі SQL запити через psycopg2 (без ORM).
    """

    def __init__(self):
        """Ініціалізація репозиторію."""
        self.db = get_db()
        self.table_name = "t_students"
        self.view_name = "v_student_full_info"

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Створити нового студента.

        Args:
            data: Словник з даними студента
                Обов'язкові поля: last_name, first_name, student_id_number,
                                 group_id, email, birth_date

        Returns:
            Optional[int]: ID створеного студента або None
        """
        query = f"""
            INSERT INTO {self.table_name} (
                last_name, first_name, patronymic, student_id_number,
                group_id, email, phone, birth_date, enrollment_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE)
            )
            RETURNING id;
        """

        params = (
            data.get('last_name'),
            data.get('first_name'),
            data.get('patronymic'),
            data.get('student_id_number'),
            data.get('group_id'),
            data.get('email'),
            data.get('phone'),
            data.get('birth_date'),
            data.get('enrollment_date')
        )

        try:
            return self.db.execute_insert(query, params)
        except PostgresError as e:
            logger.error(f"Error creating student: {e}")
            raise

    def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Отримати студента за ID з повною інформацією (VIEW).

        Args:
            student_id: ID студента

        Returns:
            Optional[Dict[str, Any]]: Дані студента з VIEW або None
        """
        query = f"""
            SELECT * FROM {self.view_name}
            WHERE id = %s;
        """

        try:
            return self.db.execute_one(query, (student_id,))
        except PostgresError as e:
            logger.error(f"Error getting student by id: {e}")
            return None

    def get_by_student_id_number(self, student_id_number: str) -> Optional[Dict[str, Any]]:
        """
        Отримати студента за номером залікової книжки з повною інформацією (VIEW).

        Args:
            student_id_number: Номер залікової книжки студента

        Returns:
            Optional[Dict[str, Any]]: Дані студента з VIEW або None
        """
        query = f"""
            SELECT * FROM {self.view_name}
            WHERE student_id_number = %s;
        """

        try:
            return self.db.execute_one(query, (student_id_number,))
        except PostgresError as e:
            logger.error(f"Error getting student by student_id_number: {e}")
            return None

    def get_all(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Отримати всіх студентів з пагінацією.

        Args:
            offset: Зміщення
            limit: Кількість записів (макс 100)

        Returns:
            List[Dict[str, Any]]: Список студентів з повною інформацією
        """
        limit = min(limit, 100)  # Обмеження для безпеки

        query = f"""
            SELECT * FROM {self.view_name}
            ORDER BY last_name, first_name
            LIMIT %s OFFSET %s;
        """

        try:
            return self.db.execute_query(query, (limit, offset))
        except PostgresError as e:
            logger.error(f"Error getting all students: {e}")
            return []

    def search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Пошук студентів за критеріями.

        Args:
            params: Словник з параметрами пошуку
                - query: загальний пошук (last_name, email, group_name)
                - group_name: фільтр за групою
                - specialty_code: фільтр за спеціальністю
                - course_number: фільтр за курсом
                - offset: зміщення
                - limit: кількість записів

        Returns:
            List[Dict[str, Any]]: Список знайдених студентів
        """
        conditions = []
        values = []

        # General search query (last_name, email, group_name)
        if params.get('query'):
            search_pattern = f"%{params['query']}%"
            conditions.append("""(
                last_name ILIKE %s OR
                email ILIKE %s OR
                group_name ILIKE %s
            )""")
            values.extend([search_pattern, search_pattern, search_pattern])

        # Filter by group name
        if params.get('group_name'):
            conditions.append("group_name = %s")
            values.append(params['group_name'])

        # Filter by specialty code
        if params.get('specialty_code'):
            conditions.append("specialty_code = %s")
            values.append(params['specialty_code'])

        # Filter by course number
        if params.get('course_number'):
            conditions.append("course_number = %s")
            values.append(params['course_number'])

        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Pagination
        offset = params.get('offset', 0)
        limit = min(params.get('limit', 50), 100)

        query = f"""
            SELECT * FROM {self.view_name}
            {where_clause}
            ORDER BY last_name, first_name
            LIMIT %s OFFSET %s;
        """

        values.extend([limit, offset])

        try:
            return self.db.execute_query(query, tuple(values))
        except PostgresError as e:
            logger.error(f"Error searching students: {e}")
            return []

    def update(self, student_id: int, data: Dict[str, Any]) -> bool:
        """
        Оновити дані студента.

        Args:
            student_id: ID студента
            data: Словник з полями для оновлення

        Returns:
            bool: True якщо оновлення успішне
        """
        # Build SET clause dynamically
        set_parts = []
        values = []

        allowed_fields = [
            'last_name', 'first_name', 'patronymic', 'student_id_number',
            'group_id', 'email', 'phone', 'birth_date'
        ]

        for field in allowed_fields:
            if field in data:
                set_parts.append(f"{field} = %s")
                values.append(data[field])

        if not set_parts:
            return False  # Nothing to update

        set_clause = ", ".join(set_parts)
        values.append(student_id)

        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE id = %s;
        """

        try:
            rows_affected = self.db.execute_update(query, tuple(values))
            return rows_affected > 0
        except PostgresError as e:
            logger.error(f"Error updating student: {e}")
            raise

    def delete(self, student_id: int) -> bool:
        """
        Видалити студента.

        Args:
            student_id: ID студента

        Returns:
            bool: True якщо видалення успішне
        """
        query = f"""
            DELETE FROM {self.table_name}
            WHERE id = %s;
        """

        try:
            rows_affected = self.db.execute_update(query, (student_id,))
            return rows_affected > 0
        except PostgresError as e:
            logger.error(f"Error deleting student: {e}")
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Порахувати кількість студентів.

        Args:
            filters: Опціональні фільтри для підрахунку

        Returns:
            int: Кількість студентів
        """
        conditions = []
        values = []

        if filters:
            if filters.get('group_name'):
                conditions.append("group_name = %s")
                values.append(filters['group_name'])

            if filters.get('course_number'):
                conditions.append("course_number = %s")
                values.append(filters['course_number'])

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT COUNT(*) as count FROM {self.view_name}
            {where_clause};
        """

        try:
            result = self.db.execute_one(query, tuple(values) if values else None)
            return result['count'] if result else 0
        except PostgresError as e:
            logger.error(f"Error counting students: {e}")
            return 0

    def exists(self, student_id: int) -> bool:
        """
        Перевірити чи існує студент.

        Args:
            student_id: ID студента

        Returns:
            bool: True якщо студент існує
        """
        query = f"""
            SELECT EXISTS(
                SELECT 1 FROM {self.table_name}
                WHERE id = %s
            ) as exists;
        """

        try:
            result = self.db.execute_one(query, (student_id,))
            return result['exists'] if result else False
        except PostgresError as e:
            logger.error(f"Error checking student existence: {e}")
            return False

    def exists_by_student_id_number(self, student_id_number: str, exclude_id: Optional[int] = None) -> bool:
        """
        Перевірити чи існує студент з таким номером залікової книжки.

        Args:
            student_id_number: Номер залікової книжки
            exclude_id: ID студента що виключається з перевірки (для update)

        Returns:
            bool: True якщо номер вже використовується
        """
        conditions = ["student_id_number = %s"]
        values = [student_id_number]

        if exclude_id:
            conditions.append("id != %s")
            values.append(exclude_id)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT EXISTS(
                SELECT 1 FROM {self.table_name}
                WHERE {where_clause}
            ) as exists;
        """

        try:
            result = self.db.execute_one(query, tuple(values))
            return result['exists'] if result else False
        except PostgresError as e:
            logger.error(f"Error checking student ID number: {e}")
            return False

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх груп.

        Returns:
            List[Dict[str, Any]]: Список груп
        """
        query = """
            SELECT id, name, specialty_id, course_id, admission_year
            FROM t_groups
            ORDER BY name;
        """

        try:
            return self.db.execute_query(query)
        except PostgresError as e:
            logger.error(f"Error getting groups: {e}")
            return []

    def get_all_specialties(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх спеціальностей.

        Returns:
            List[Dict[str, Any]]: Список спеціальностей
        """
        query = """
            SELECT id, name, code, description
            FROM t_specialties
            ORDER BY name;
        """

        try:
            return self.db.execute_query(query)
        except PostgresError as e:
            logger.error(f"Error getting specialties: {e}")
            return []

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх курсів.

        Returns:
            List[Dict[str, Any]]: Список курсів
        """
        query = """
            SELECT id, course_number, name
            FROM t_courses
            ORDER BY course_number;
        """

        try:
            return self.db.execute_query(query)
        except PostgresError as e:
            logger.error(f"Error getting courses: {e}")
            return []

    def exists_student_id(self, student_id_number: str) -> bool:
        """
        Перевірити чи існує студент з таким номером залікової книжки.

        Alias для exists_by_student_id_number для зручності використання в seed.

        Args:
            student_id_number: Номер залікової книжки

        Returns:
            bool: True якщо номер вже використовується
        """
        return self.exists_by_student_id_number(student_id_number)

    def count_by_course(self, course_id: int) -> int:
        """
        Порахувати кількість студентів на курсі.

        Args:
            course_id: ID курсу

        Returns:
            int: Кількість студентів
        """
        query = """
            SELECT COUNT(*) as count
            FROM v_student_full_info
            WHERE course_id = %s;
        """

        try:
            result = self.db.execute_one(query, (course_id,))
            return result['count'] if result else 0
        except PostgresError as e:
            logger.error(f"Error counting students by course: {e}")
            return 0
