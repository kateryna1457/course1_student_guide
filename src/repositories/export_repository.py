"""
Репозиторій для експорту даних з PostgreSQL у файли.

Підтримує експорт у JSON та CSV формати.
"""

import logging
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
import tempfile
import os

from .database import get_db

logger = logging.getLogger(__name__)


class ExportRepository:
    """
    Репозиторій для експорту даних з бази даних у файли.

    Підтримувані формати: JSON, CSV
    """

    def __init__(self):
        """Ініціалізація репозиторію."""
        self.db = get_db()
        self.view_name = "v_student_full_info"

    def _get_all_students(self) -> List[Dict[str, Any]]:
        """
        Отримати всіх студентів з VIEW.

        Returns:
            List[Dict[str, Any]]: Список всіх студентів
        """
        query = f"""
            SELECT * FROM {self.view_name}
            ORDER BY last_name, first_name;
        """
        return self.db.execute_query(query)

    def _atomic_write(self, target_path: str, content: str, mode: str = 'w', encoding: str = 'utf-8'):
        """
        Атомарний запис у файл (через тимчасовий файл).

        Args:
            target_path: Цільовий шлях файлу
            content: Контент для запису
            mode: Режим запису ('w' або 'wb')
            encoding: Кодування файлу (за замовчуванням 'utf-8')
        """
        # Create directory if not exists
        target_dir = os.path.dirname(target_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        # Write to temporary file first
        temp_fd, temp_path = tempfile.mkstemp(dir=target_dir, suffix='.tmp')

        try:
            with os.fdopen(temp_fd, mode, encoding=encoding if mode == 'w' else None) as f:
                f.write(content)

            # Atomic rename
            os.replace(temp_path, target_path)

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    def export_to_json(self, file_path: str) -> int:
        """
        Експортувати всіх студентів у JSON файл.

        Args:
            file_path: Шлях до файлу для збереження

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилках запису
        """
        students = self._get_all_students()
        return self._write_json(file_path, students)

    def export_students_to_json(self, file_path: str, students: List[Any]) -> int:
        """
        Експортувати певний список студентів у JSON файл.

        Args:
            file_path: Шлях до файлу для збереження
            students: Список студентів (StudentFullInfo objects)

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилках запису
        """
        # Convert StudentFullInfo objects to dicts
        students_data = [s.to_dict() for s in students]
        return self._write_json(file_path, students_data)

    def _write_json(self, file_path: str, students: List[Dict[str, Any]]) -> int:
        """
        Записати студентів у JSON файл.

        Args:
            file_path: Шлях до файлу
            students: Список студентів (dicts)

        Returns:
            int: Кількість експортованих записів
        """
        # Convert date objects to ISO format strings
        for student in students:
            if student.get('birth_date'):
                if not isinstance(student['birth_date'], str):
                    student['birth_date'] = student['birth_date'].isoformat()
            if student.get('enrollment_date'):
                if not isinstance(student['enrollment_date'], str):
                    student['enrollment_date'] = student['enrollment_date'].isoformat()

        # Create JSON with pretty formatting
        json_content = json.dumps(
            {
                "metadata": {
                    "total_count": len(students),
                    "format": "json",
                    "version": "1.0"
                },
                "students": students
            },
            indent=2,
            ensure_ascii=False,  # Підтримка кирилиці
            default=str
        )

        self._atomic_write(file_path, json_content, 'w')
        logger.info(f"Exported {len(students)} students to {file_path}")

        return len(students)

    def export_to_csv(self, file_path: str) -> int:
        """
        Експортувати всіх студентів у CSV файл.

        Args:
            file_path: Шлях до файлу для збереження

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилках запису
        """
        students = self._get_all_students()
        return self._write_csv(file_path, students)

    def export_students_to_csv(self, file_path: str, students: List[Any]) -> int:
        """
        Експортувати певний список студентів у CSV файл.

        Args:
            file_path: Шлях до файлу для збереження
            students: Список студентів (StudentFullInfo objects)

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилках запису
        """
        # Convert StudentFullInfo objects to dicts
        students_data = [s.to_dict() for s in students]
        return self._write_csv(file_path, students_data)

    def _write_csv(self, file_path: str, students: List[Dict[str, Any]]) -> int:
        """
        Записати студентів у CSV файл з UTF-8 BOM.

        Args:
            file_path: Шлях до файлу
            students: Список студентів (dicts)

        Returns:
            int: Кількість експортованих записів
        """
        csv_content = self._create_csv_content(students)

        # Write CSV with UTF-8 BOM for Excel compatibility
        # Create directory if not exists
        target_dir = os.path.dirname(file_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        # Write to temporary file first with explicit UTF-8 BOM
        temp_fd, temp_path = tempfile.mkstemp(dir=target_dir, suffix='.tmp')

        try:
            # Write as binary with UTF-8 BOM (0xEF, 0xBB, 0xBF)
            with os.fdopen(temp_fd, 'wb') as f:
                # Write UTF-8 BOM
                f.write(b'\xef\xbb\xbf')
                # Write CSV content as UTF-8 bytes
                f.write(csv_content.encode('utf-8'))

            # Atomic rename
            os.replace(temp_path, file_path)

            logger.info(f"Exported {len(students)} students to {file_path}")
            return len(students)

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    def _create_csv_content(self, students: List[Dict[str, Any]]) -> str:
        """
        Створити CSV контент зі списку студентів з UTF-8 BOM для підтримки кирилиці.

        Args:
            students: Список студентів

        Returns:
            str: CSV контент з UTF-8 BOM
        """
        # Define CSV columns
        fieldnames = [
            'id',
            'last_name',
            'first_name',
            'patronymic',
            'student_id_number',
            'email',
            'phone',
            'birth_date',
            'enrollment_date',
            'group_name',
            'admission_year',
            'course_number',
            'course_name',
            'specialty_name',
            'specialty_code',
            'specialty_description'
        ]

        # Create CSV in memory with UTF-8 BOM for Excel compatibility
        import io
        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            extrasaction='ignore',
            delimiter=';',  # Use semicolon for Excel compatibility with Cyrillic
            quoting=csv.QUOTE_MINIMAL
        )

        writer.writeheader()

        for student in students:
            # Convert dates to ISO format (only if they're not already strings)
            row = dict(student)
            if row.get('birth_date'):
                if not isinstance(row['birth_date'], str):
                    row['birth_date'] = row['birth_date'].isoformat()
            if row.get('enrollment_date'):
                if not isinstance(row['enrollment_date'], str):
                    row['enrollment_date'] = row['enrollment_date'].isoformat()

            writer.writerow(row)

        return output.getvalue()

    def get_export_stats(self) -> Dict[str, Any]:
        """
        Отримати статистику для експорту.

        Returns:
            Dict[str, Any]: Статистика (кількість студентів, груп, тощо)
        """
        stats = {}

        # Count students
        query_students = f"SELECT COUNT(*) as count FROM {self.view_name};"
        result = self.db.execute_one(query_students)
        stats['total_students'] = result['count'] if result else 0

        # Count groups
        query_groups = "SELECT COUNT(*) as count FROM t_groups;"
        result = self.db.execute_one(query_groups)
        stats['total_groups'] = result['count'] if result else 0

        # Count specialties
        query_specialties = "SELECT COUNT(*) as count FROM t_specialties;"
        result = self.db.execute_one(query_specialties)
        stats['total_specialties'] = result['count'] if result else 0

        # Count by course
        query_by_course = """
            SELECT course_number, COUNT(*) as count
            FROM v_student_full_info
            GROUP BY course_number
            ORDER BY course_number;
        """
        stats['students_by_course'] = self.db.execute_query(query_by_course)

        return stats
