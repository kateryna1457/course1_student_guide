from typing import Optional
from dataclasses import dataclass


@dataclass
class Specialty:
    """
    Клас для представлення академічної спеціальності.

    Attributes:
        id: Унікальний ідентифікатор спеціальності
        name: Повна назва спеціальності
        code: Код спеціальності (наприклад, '121', '122')
        description: Опис спеціальності
    """

    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Валідація після ініціалізації."""
        if self.code is not None and len(self.code) < 2:
            raise ValueError(f"Specialty code must be at least 2 characters, got '{self.code}'")

    def to_dict(self) -> dict:
        """
        Перетворити об'єкт у словник.

        Returns:
            dict: Словник з атрибутами спеціальності
        """
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Specialty":
        """
        Створити об'єкт Specialty зі словника.

        Args:
            data: Словник з даними спеціальності

        Returns:
            Specialty: Новий об'єкт Specialty
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            code=data.get("code"),
            description=data.get("description")
        )

    def __str__(self) -> str:
        """
        Строкове представлення спеціальності.

        Returns:
            str: Строка з інформацією про спеціальність
        """
        if self.code:
            return f"{self.name} ({self.code})"
        return f"{self.name}"

    def __repr__(self) -> str:
        """
        Технічне представлення спеціальності.

        Returns:
            str: Технічне представлення об'єкта
        """
        return f"Specialty(id={self.id}, name='{self.name}', code='{self.code}')"
