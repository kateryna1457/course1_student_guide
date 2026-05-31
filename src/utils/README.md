# Utils Module - Validators

Модуль валідації даних для перевірки коректності введених даних.

## Валідатори

### 1. `validate_student_id_number(student_id: str)`

Перевіряє формат номера залікової книжки.

**Підтримувані формати:**
- `XX-NNNN` (наприклад, `CS-2024`, `SE-0001`)
- `XXNNNN` (наприклад, `CS2024`)
- `XXX-NNNN` (наприклад, `CSC-2024`)

**Приклад:**
```python
from src.utils import validate_student_id_number, ValidationError

try:
    validate_student_id_number("CS-2024")  # ✓ Valid
    validate_student_id_number("SE2024")   # ✓ Valid
    validate_student_id_number("123")      # ✗ Invalid - raises ValidationError
except ValidationError as e:
    print(f"Error: {e}")
```

### 2. `validate_group_name(group_name: str)`

Перевіряє формат назви групи.

**Формат:** `XX-NN` (2-4 літери, дефіс, 1-2 цифри)

**Приклади:**
- ✓ `CS-11`, `SE-21`, `IT-31`
- ✗ `CS11`, `C-1`

### 3. `validate_course_number(course_number: int)`

Перевіряє номер курсу (1-6).

**Приклад:**
```python
validate_course_number(1)  # ✓ Valid
validate_course_number(6)  # ✓ Valid
validate_course_number(7)  # ✗ Invalid
```

### 4. `validate_email(email: str)`

Перевіряє формат електронної пошти (RFC 5322).

**Приклади:**
- ✓ `student@example.com`
- ✓ `john.doe@university.edu.ua`
- ✗ `notanemail`

### 5. `validate_phone(phone: str)`

Перевіряє український номер телефону.

**Підтримувані формати:**
- `+380XXXXXXXXX` (міжнародний)
- `0XXXXXXXXX` (національний)
- `(0XX) XXX-XX-XX` (з форматуванням)

**Приклади:**
- ✓ `+380501234567`
- ✓ `0501234567`
- ✓ `(050) 123-45-67`

### 6. `validate_birth_date(birth_date: date, min_age=15, max_age=100)`

Перевіряє дату народження та вік.

**Параметри:**
- `min_age` - мінімальний вік (за замовчуванням 15)
- `max_age` - максимальний вік (за замовчуванням 100)

**Приклад:**
```python
from datetime import date

validate_birth_date(date(2000, 1, 1))  # ✓ Valid
validate_birth_date(date(2020, 1, 1))  # ✗ Too young
```

### 7. `validate_specialty_code(code: str)`

Перевіряє код спеціальності.

**Формат:** `NNN` або `NNN-XX` (3 цифри опціонально з дефісом та 1-4 літерами)

**Приклади:**
- ✓ `121`, `122`, `122-DS`, `122-AI`
- ✗ `12`, `ABC`

### 8. `validate_admission_year(admission_year: int)`

Перевіряє рік вступу (1900 - поточний рік + 1).

### 9. `validate_not_empty(value: str, field_name: str)`

Перевіряє що поле не порожнє.

### 10. `validate_string_length(value: str, field_name: str, min_length=1, max_length=255)`

Перевіряє довжину рядка.

### 11. `validate_student_data(...)`

Комплексна валідація всіх даних студента одночасно.

**Приклад:**
```python
from datetime import date
from src.utils import validate_student_data, ValidationError

try:
    validate_student_data(
        last_name="Shevchenko",
        first_name="Taras",
        student_id_number="CS-2024",
        email="shevchenko@example.com",
        birth_date=date(2000, 1, 1),
        patronymic="Hryhorovych",
        phone="+380501234567"
    )
    print("All data is valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## ValidationError

Всі валідатори викидають `ValidationError` при невалідних даних.

```python
from src.utils import ValidationError

try:
    # some validation
    pass
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Тестування

Запустити демонстраційні тести:

```bash
python tests/test_validators_demo.py
```

## Використання в проекті

Валідатори використовуються:
1. **В OOP моделях** - для перевірки в `__post_init__`
2. **В Pydantic схемах** - через `@field_validator`
3. **В репозиторіях** - перед збереженням в БД
4. **В сервісах** - для бізнес-логіки валідації

## Приклад інтеграції

```python
from src.models import Student
from src.utils import validate_student_data, ValidationError
from datetime import date

# Перевірка даних перед створенням об'єкта
try:
    validate_student_data(
        last_name="Ivanov",
        first_name="Ivan",
        student_id_number="CS-2024",
        email="ivanov@example.com",
        birth_date=date(2001, 5, 15)
    )
    
    # Якщо валідація пройшла - створюємо об'єкт
    student = Student(
        last_name="Ivanov",
        first_name="Ivan",
        student_id_number="CS-2024",
        email="ivanov@example.com",
        birth_date=date(2001, 5, 15),
        group_id=1
    )
    
except ValidationError as e:
    print(f"Cannot create student: {e}")
```
