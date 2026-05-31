"""
OOP модель для групи студентів.

Цей модуль містить клас Group, що представляє студентську групу.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Group:
    """
    Клас для представлення студентської групи.

    Attributes:
        id: Унікальний ідентифікатор групи
        name: Назва групи (наприклад, 'CS-11', 'SE-21')
        specialty_id: ID спеціальності
        course_id: ID курсу
        admission_year: Рік вступу групи
    """

    id: Optional[int] = None
    name: Optional[str] = None
    specialty_id: Optional[int] = None
    course_id: Optional[int] = None
    admission_year: Optional[int] = None

    def __post_init__(self):
        """Валідація після ініціалізації."""
        if self.admission_year is not None:
            if not (1900 <= self.admission_year <= 2100):
                raise ValueError(
                    f"Admission year must be between 1900 and 2100, got {self.admission_year}"
                )

    def to_dict(self) -> dict:
        """
        Перетворити об'єкт у словник.

        Returns:
            dict: Словник з атрибутами групи
        """
        return {
            "id": self.id,
            "name": self.name,
            "specialty_id": self.specialty_id,
            "course_id": self.course_id,
            "admission_year": self.admission_year
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Group":
        """
        Створити об'єкт Group зі словника.

        Args:
            data: Словник з даними групи

        Returns:
            Group: Новий об'єкт Group
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            specialty_id=data.get("specialty_id"),
            course_id=data.get("course_id"),
            admission_year=data.get("admission_year")
        )

    def __str__(self) -> str:
        """
        Строкове представлення групи.

        Returns:
            str: Строка з інформацією про групу
        """
        return f"Group {self.name} ({self.admission_year})"

    def __repr__(self) -> str:
        """
        Технічне представлення групи.

        Returns:
            str: Технічне представлення об'єкта
        """
        return (
            f"Group(id={self.id}, name='{self.name}', "
            f"specialty_id={self.specialty_id}, course_id={self.course_id}, "
            f"admission_year={self.admission_year})"
        )
