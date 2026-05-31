from typing import Optional
from datetime import date
from dataclasses import dataclass, field


@dataclass
class Student:
    """
    Клас для представлення студента.

    Attributes:
        id: Унікальний ідентифікатор студента
        last_name: Прізвище
        first_name: Ім'я
        patronymic: По батькові (опціонально)
        student_id_number: Номер залікової книжки
        group_id: ID групи
        email: Електронна пошта
        phone: Номер телефону (опціонально)
        birth_date: Дата народження
        enrollment_date: Дата зарахування
    """

    id: Optional[int] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    patronymic: Optional[str] = None
    student_id_number: Optional[str] = None
    group_id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    enrollment_date: Optional[date] = field(default_factory=lambda: date.today())

    def get_full_name(self) -> str:
        """
        Отримати повне ім'я студента.

        Returns:
            str: Повне ім'я (Прізвище Ім'я По-батькові)
        """
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(filter(None, parts))

    def to_dict(self) -> dict:
        """
        Перетворити об'єкт у словник.

        Returns:
            dict: Словник з атрибутами студента
        """
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "patronymic": self.patronymic,
            "student_id_number": self.student_id_number,
            "group_id": self.group_id,
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Створити об'єкт Student зі словника.

        Args:
            data: Словник з даними студента

        Returns:
            Student: Новий об'єкт Student
        """
        # Convert string dates to date objects if needed
        birth_date = data.get("birth_date")
        if isinstance(birth_date, str):
            birth_date = date.fromisoformat(birth_date)

        enrollment_date = data.get("enrollment_date")
        if isinstance(enrollment_date, str):
            enrollment_date = date.fromisoformat(enrollment_date)

        return cls(
            id=data.get("id"),
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            patronymic=data.get("patronymic"),
            student_id_number=data.get("student_id_number"),
            group_id=data.get("group_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            birth_date=birth_date,
            enrollment_date=enrollment_date
        )

    def __str__(self) -> str:
        """
        Строкове представлення студента.

        Returns:
            str: Строка з інформацією про студента
        """
        return f"{self.get_full_name()} ({self.student_id_number})"

    def __repr__(self) -> str:
        """
        Технічне представлення студента.

        Returns:
            str: Технічне представлення об'єкта
        """
        return (
            f"Student(id={self.id}, name='{self.get_full_name()}', "
            f"student_id_number='{self.student_id_number}', email='{self.email}')"
        )


@dataclass
class StudentFullInfo(Student):
    """
    Розширений клас студента з повною інформацією (з JOIN).

    Додаткові атрибути з VIEW v_student_full_info:
        group_name: Назва групи
        admission_year: Рік вступу групи
        course_number: Номер курсу
        course_name: Назва курсу
        specialty_name: Назва спеціальності
        specialty_code: Код спеціальності
        specialty_description: Опис спеціальності
    """

    group_name: Optional[str] = None
    admission_year: Optional[int] = None
    course_number: Optional[int] = None
    course_name: Optional[str] = None
    specialty_name: Optional[str] = None
    specialty_code: Optional[str] = None
    specialty_description: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Перетворити об'єкт у словник з повною інформацією.

        Returns:
            dict: Словник з усіма атрибутами
        """
        base_dict = super().to_dict()
        base_dict.update({
            "group_name": self.group_name,
            "admission_year": self.admission_year,
            "course_number": self.course_number,
            "course_name": self.course_name,
            "specialty_name": self.specialty_name,
            "specialty_code": self.specialty_code,
            "specialty_description": self.specialty_description
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "StudentFullInfo":
        """
        Створити об'єкт StudentFullInfo зі словника.

        Args:
            data: Словник з повними даними студента

        Returns:
            StudentFullInfo: Новий об'єкт StudentFullInfo
        """
        # Convert string dates to date objects if needed
        birth_date = data.get("birth_date")
        if isinstance(birth_date, str):
            birth_date = date.fromisoformat(birth_date)

        enrollment_date = data.get("enrollment_date")
        if isinstance(enrollment_date, str):
            enrollment_date = date.fromisoformat(enrollment_date)

        return cls(
            id=data.get("id"),
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            patronymic=data.get("patronymic"),
            student_id_number=data.get("student_id_number"),
            group_id=data.get("group_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            birth_date=birth_date,
            enrollment_date=enrollment_date,
            group_name=data.get("group_name"),
            admission_year=data.get("admission_year"),
            course_number=data.get("course_number"),
            course_name=data.get("course_name"),
            specialty_name=data.get("specialty_name"),
            specialty_code=data.get("specialty_code"),
            specialty_description=data.get("specialty_description")
        )

    def __str__(self) -> str:
        """
        Строкове представлення студента з повною інформацією.

        Returns:
            str: Детальна строка з інформацією
        """
        return (
            f"{self.get_full_name()} ({self.student_id_number}) - "
            f"{self.group_name}, {self.specialty_name}"
        )
