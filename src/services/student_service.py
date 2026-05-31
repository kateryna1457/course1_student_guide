from typing import Optional, List, Dict, Any
from datetime import date
from psycopg2 import Error as PostgresError

from src.models import StudentFullInfo
from src.repositories import StudentRepository, ExportRepository
from src.utils import (
    validate_student_data,
    validate_email,
    validate_phone,
    validate_birth_date,
    ValidationError
)


class StudentService:
    """
    Сервіс для роботи зі студентами.

    Містить бізнес-логіку, валідацію та використовує репозиторії.
    """

    def __init__(
        self,
        student_repository: Optional[StudentRepository] = None,
        export_repository: Optional[ExportRepository] = None
    ):
        """
        Ініціалізація сервісу.

        Args:
            student_repository: Репозиторій студентів (dependency injection)
            export_repository: Репозиторій експорту (dependency injection)
        """
        self.student_repo = student_repository or StudentRepository()
        self.export_repo = export_repository or ExportRepository()

    def create_student(self, data: Dict[str, Any]) -> int:
        """
        Створити нового студента з валідацією.

        Args:
            data: Дані студента

        Returns:
            int: ID створеного студента

        Raises:
            ValidationError: При невалідних даних
            ValueError: При дублюванні student_id_number
            PostgresError: При помилці БД
        """
        required_fields = ['last_name', 'first_name', 'student_id_number', 'group_id', 'email', 'birth_date']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Field '{field}' is required")

        birth_date = data.get('birth_date')
        if isinstance(birth_date, str):
            birth_date = date.fromisoformat(birth_date)

        validate_student_data(
            last_name=data['last_name'],
            first_name=data['first_name'],
            student_id_number=data['student_id_number'],
            email=data['email'],
            birth_date=birth_date,
            patronymic=data.get('patronymic'),
            phone=data.get('phone')
        )

        if self.student_repo.exists_by_student_id_number(data['student_id_number']):
            raise ValueError(
                f"Student with ID number '{data['student_id_number']}' already exists"
            )

        student_id = self.student_repo.create(data)

        if not student_id:
            raise PostgresError("Failed to create student")

        return student_id

    def get_student(self, student_id: int) -> Optional[StudentFullInfo]:
        """
        Отримати студента за ID з повною інформацією.

        Args:
            student_id: ID студента

        Returns:
            Optional[StudentFullInfo]: Об'єкт студента або None

        Raises:
            ValueError: Якщо student_id <= 0
        """
        if student_id <= 0:
            raise ValueError("Student ID must be greater than 0")

        data = self.student_repo.get_by_id(student_id)

        if not data:
            return None

        return StudentFullInfo.from_dict(data)

    def get_student_by_id_number(self, student_id_number: str) -> Optional[StudentFullInfo]:
        """
        Отримати студента за номером залікової книжки з повною інформацією.

        Args:
            student_id_number: Номер залікової книжки

        Returns:
            Optional[StudentFullInfo]: Об'єкт студента або None

        Raises:
            ValueError: Якщо student_id_number порожній
        """
        if not student_id_number or not student_id_number.strip():
            raise ValueError("Student ID number cannot be empty")

        data = self.student_repo.get_by_student_id_number(student_id_number.strip())

        if not data:
            return None

        return StudentFullInfo.from_dict(data)

    def list_students(
        self,
        offset: int = 0,
        limit: int = 50
    ) -> tuple[List[StudentFullInfo], int]:
        """
        Отримати список студентів з пагінацією.

        Args:
            offset: Зміщення (за замовчуванням 0)
            limit: Кількість записів (за замовчуванням 50, максимум 100)

        Returns:
            tuple: (список студентів, загальна кількість)
        """
        if offset < 0:
            offset = 0

        if limit <= 0:
            limit = 50

        limit = min(limit, 100)

        # Get students
        data_list = self.student_repo.get_all(offset=offset, limit=limit)
        students = [StudentFullInfo.from_dict(data) for data in data_list]

        total = self.student_repo.count()

        return students, total

    def search_students(self, search_params: Dict[str, Any]) -> tuple[List[StudentFullInfo], int]:
        """
        Пошук студентів за критеріями.

        Args:
            search_params: Параметри пошуку
                - query: загальний пошук
                - group_name: фільтр за групою
                - specialty_code: фільтр за спеціальністю
                - course_number: фільтр за курсом
                - offset: зміщення
                - limit: кількість

        Returns:
            tuple: (список знайдених студентів, загальна кількість)
        """
        params = {
            'offset': max(0, search_params.get('offset', 0)),
            'limit': min(search_params.get('limit', 50), 100)
        }

        if search_params.get('query'):
            params['query'] = search_params['query'].strip()

        if search_params.get('group_name'):
            params['group_name'] = search_params['group_name'].strip()

        if search_params.get('specialty_code'):
            params['specialty_code'] = search_params['specialty_code'].strip()

        if search_params.get('course_number'):
            course = search_params['course_number']
            if 1 <= course <= 6:
                params['course_number'] = course

        data_list = self.student_repo.search(params)
        students = [StudentFullInfo.from_dict(data) for data in data_list]

        total = len(students)

        return students, total

    def update_student(self, student_id: int, data: Dict[str, Any]) -> bool:
        """
        Оновити дані студента з валідацією.

        Args:
            student_id: ID студента
            data: Дані для оновлення

        Returns:
            bool: True якщо оновлення успішне

        Raises:
            ValueError: Якщо студент не існує або дані невалідні
            ValidationError: При невалідних даних
        """
        if not self.student_repo.exists(student_id):
            raise ValueError(f"Student with ID {student_id} does not exist")

        if 'email' in data and data['email']:
            validate_email(data['email'])

        if 'phone' in data and data['phone']:
            validate_phone(data['phone'])

        if 'birth_date' in data and data['birth_date']:
            birth_date = data['birth_date']
            if isinstance(birth_date, str):
                birth_date = date.fromisoformat(birth_date)
            validate_birth_date(birth_date)

        if 'student_id_number' in data and data['student_id_number']:
            if self.student_repo.exists_by_student_id_number(
                data['student_id_number'],
                exclude_id=student_id
            ):
                raise ValueError(
                    f"Student with ID number '{data['student_id_number']}' already exists"
                )

        return self.student_repo.update(student_id, data)

    def update_student_by_id_number(self, student_id_number: str, data: Dict[str, Any]) -> bool:
        """
        Оновити дані студента за номером залікової книжки з валідацією.

        Args:
            student_id_number: Номер залікової книжки студента
            data: Дані для оновлення (тільки ті поля які змінюються)

        Returns:
            bool: True якщо оновлення успішне

        Raises:
            ValueError: Якщо студент не існує або дані невалідні
            ValidationError: При невалідних даних
        """
        student = self.get_student_by_id_number(student_id_number)
        if not student:
            raise ValueError(f"Student with ID number '{student_id_number}' does not exist")

        if 'email' in data and data['email']:
            validate_email(data['email'])

        if 'phone' in data and data['phone']:
            validate_phone(data['phone'])

        if 'birth_date' in data and data['birth_date']:
            birth_date = data['birth_date']
            if isinstance(birth_date, str):
                birth_date = date.fromisoformat(birth_date)
            validate_birth_date(birth_date)

        if 'student_id_number' in data and data['student_id_number']:
            if data['student_id_number'] != student_id_number:
                if self.student_repo.exists_by_student_id_number(
                    data['student_id_number'],
                    exclude_id=student.id
                ):
                    raise ValueError(
                        f"Student with ID number '{data['student_id_number']}' already exists"
                    )

        return self.student_repo.update(student.id, data)

    def delete_student(self, student_id: int) -> bool:
        """
        Видалити студента.

        Args:
            student_id: ID студента

        Returns:
            bool: True якщо видалення успішне

        Raises:
            ValueError: Якщо студент не існує
        """
        if not self.student_repo.exists(student_id):
            raise ValueError(f"Student with ID {student_id} does not exist")

        return self.student_repo.delete(student_id)

    def delete_student_by_id_number(self, student_id_number: str) -> bool:
        """
        Видалити студента за номером залікової книжки.

        Args:
            student_id_number: Номер залікової книжки студента

        Returns:
            bool: True якщо видалення успішне

        Raises:
            ValueError: Якщо студент не існує
        """
        student = self.get_student_by_id_number(student_id_number)
        if not student:
            raise ValueError(f"Student with ID number '{student_id_number}' does not exist")

        return self.student_repo.delete(student.id)

    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх груп.

        Returns:
            List[Dict[str, Any]]: Список груп
        """
        return self.student_repo.get_all_groups()

    def get_specialties(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх спеціальностей.

        Returns:
            List[Dict[str, Any]]: Список спеціальностей
        """
        return self.student_repo.get_all_specialties()

    def get_courses(self) -> List[Dict[str, Any]]:
        """
        Отримати список всіх курсів.

        Returns:
            List[Dict[str, Any]]: Список курсів
        """
        return self.student_repo.get_all_courses()

    def export_to_json(self, file_path: str, search_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Експортувати студентів у JSON файл з можливістю фільтрації.

        Args:
            file_path: Шлях до файлу
            search_params: Параметри фільтрації (query, group_name, specialty_code, course_number)

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилці запису
        """
        if search_params:
            students, _ = self.search_students(search_params)
            return self.export_repo.export_students_to_json(file_path, students)
        else:
            return self.export_repo.export_to_json(file_path)

    def export_to_csv(self, file_path: str, search_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Експортувати студентів у CSV файл з можливістю фільтрації.

        Args:
            file_path: Шлях до файлу
            search_params: Параметри фільтрації (query, group_name, specialty_code, course_number)

        Returns:
            int: Кількість експортованих записів

        Raises:
            Exception: При помилці запису
        """
        if search_params:
            students, _ = self.search_students(search_params)
            return self.export_repo.export_students_to_csv(file_path, students)
        else:
            return self.export_repo.export_to_csv(file_path)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Отримати статистику по студентам.

        Returns:
            Dict[str, Any]: Статистика
        """
        total_students = self.student_repo.count()
        total_groups = len(self.get_groups())
        total_specialties = len(self.get_specialties())
        total_courses = len(self.get_courses())

        students_by_course = []
        for course in self.get_courses():
            count = self.student_repo.count_by_course(course['id'])
            students_by_course.append({
                'course_number': course['course_number'],
                'course_name': course['name'],
                'count': count
            })

        return {
            'total_students': total_students,
            'total_groups': total_groups,
            'total_specialties': total_specialties,
            'total_courses': total_courses,
            'students_by_course': students_by_course
        }

    def student_exists(self, student_id: int) -> bool:
        """
        Перевірити чи існує студент.

        Args:
            student_id: ID студента

        Returns:
            bool: True якщо студент існує
        """
        return self.student_repo.exists(student_id)

    def student_id_number_available(self, student_id_number: str) -> bool:
        """
        Перевірити чи доступний номер залікової книжки.

        Args:
            student_id_number: Номер залікової книжки

        Returns:
            bool: True якщо номер доступний (не використовується)
        """
        return not self.student_repo.exists_by_student_id_number(student_id_number)
