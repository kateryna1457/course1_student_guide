"""
OOP модель для курсу навчання.

Цей модуль містить клас Course, що представляє курс навчання (1-6).
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Course:
    """
    Клас для представлення курсу навчання.

    Attributes:
        id: Унікальний ідентифікатор курсу
        course_number: Номер курсу (1-6)
        name: Назва курсу (наприклад, "First Year")
    """

    id: Optional[int] = None
    course_number: Optional[int] = None
    name: Optional[str] = None

    def __post_init__(self):
        """Валідація після ініціалізації."""
        if self.course_number is not None:
            if not (1 <= self.course_number <= 6):
                raise ValueError(f"Course number must be between 1 and 6, got {self.course_number}")

    def to_dict(self) -> dict:
        """
        Перетворити об'єкт у словник.

        Returns:
            dict: Словник з атрибутами курсу
        """
        return {
            "id": self.id,
            "course_number": self.course_number,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        """
        Створити об'єкт Course зі словника.

        Args:
            data: Словник з даними курсу

        Returns:
            Course: Новий об'єкт Course
        """
        return cls(
            id=data.get("id"),
            course_number=data.get("course_number"),
            name=data.get("name")
        )

    def __str__(self) -> str:
        """
        Строкове представлення курсу.

        Returns:
            str: Строка з інформацією про курс
        """
        return f"Course {self.course_number}: {self.name}"

    def __repr__(self) -> str:
        """
        Технічне представлення курсу.

        Returns:
            str: Технічне представлення об'єкта
        """
        return f"Course(id={self.id}, course_number={self.course_number}, name='{self.name}')"
