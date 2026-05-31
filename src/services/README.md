# Services Module - Business Logic Layer

Модуль сервісів містить бізнес-логіку додатка та оркеструє роботу репозиторіїв.

## Архітектура

```
┌─────────────────────────────────────┐
│      API / CLI Layer                │
│  (Presentation)                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Service Layer                  │  ◄── Ми тут
│  (Business Logic)                   │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   StudentService             │  │
│  │   - Валідація                │  │
│  │   - Бізнес-правила          │  │
│  │   - Оркестрація репозиторіїв│  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Repository Layer               │
│  (Data Access)                      │
└─────────────────────────────────────┘
```

## StudentService

Головний сервіс для роботи зі студентами.

### Принципи

1. **Dependency Injection** - репозиторії передаються через конструктор
2. **Валідація** - перевірка даних перед збереженням
3. **Бізнес-правила** - унікальність student_id_number, існування студента
4. **Оркестрація** - використання кількох репозиторіїв
5. **Type safety** - повертає OOP моделі, не словники

### Ініціалізація

```python
from src.services import StudentService

# Використання за замовчуванням (створює власні репозиторії)
service = StudentService()

# Dependency Injection (для тестування або кастомізації)
from src.repositories import StudentRepository, ExportRepository

student_repo = StudentRepository()
export_repo = ExportRepository()
service = StudentService(
    student_repository=student_repo,
    export_repository=export_repo
)
```

### CRUD Операції

#### 1. Створення студента

```python
from datetime import date

student_data = {
    'last_name': 'Shevchenko',
    'first_name': 'Taras',
    'patronymic': 'Hryhorovych',
    'student_id_number': 'CS-2024',
    'group_id': 1,
    'email': 'shevchenko@example.com',
    'phone': '+380501234567',
    'birth_date': date(2000, 3, 9)
}

try:
    student_id = service.create_student(student_data)
    print(f"Student created with ID: {student_id}")
except ValidationError as e:
    print(f"Validation error: {e}")
except ValueError as e:
    print(f"Business rule violation: {e}")
```

**Валідація при створенні:**
- ✓ Обов'язкові поля (last_name, first_name, student_id_number, group_id, email, birth_date)
- ✓ Формат email (RFC 5322)
- ✓ Формат телефону (український)
- ✓ Формат student_id_number
- ✓ Вік (мінімум 15 років)
- ✓ Унікальність student_id_number

#### 2. Читання студента

```python
# Отримати студента з повною інформацією (VIEW)
student = service.get_student(student_id)

if student:
    print(f"Name: {student.get_full_name()}")
    print(f"Email: {student.email}")
    print(f"Group: {student.group_name}")  # З VIEW
    print(f"Specialty: {student.specialty_name}")  # З VIEW
    print(f"Course: {student.course_number}")  # З VIEW
else:
    print("Student not found")
```

**Повертає:** `StudentFullInfo` об'єкт (extends Student)

#### 3. Список студентів

```python
# Отримати список з пагінацією
students, total = service.list_students(offset=0, limit=50)

print(f"Total students: {total}")
print(f"Showing: {len(students)}")

for student in students:
    print(f"- {student.get_full_name()} ({student.student_id_number})")
```

**Параметри:**
- `offset` - зміщення (за замовчуванням 0)
- `limit` - кількість (за замовчуванням 50, максимум 100)

**Повертає:** tuple (список StudentFullInfo, загальна кількість)

#### 4. Пошук студентів

```python
# Пошук за різними критеріями
results, count = service.search_students({
    'query': 'Shevchenko',      # Загальний пошук (last_name, email, group_name)
    'group_name': 'CS-11',       # Фільтр за групою
    'specialty_code': '122',     # Фільтр за спеціальністю
    'course_number': 1,          # Фільтр за курсом
    'offset': 0,
    'limit': 20
})

print(f"Found {count} students")
for student in results:
    print(f"- {student.get_full_name()}")
```

**Параметри пошуку:**
- `query` - загальний пошук (ILIKE по last_name, email, group_name)
- `group_name` - точний фільтр за назвою групи
- `specialty_code` - фільтр за кодом спеціальності
- `course_number` - фільтр за номером курсу (1-6)
- `offset`, `limit` - пагінація

#### 5. Оновлення студента

```python
# Оновити одне або кілька полів
updated = service.update_student(student_id, {
    'email': 'new_email@example.com',
    'phone': '+380671234567'
})

if updated:
    print("Student updated successfully")
else:
    print("Update failed")
```

**Валідація при оновленні:**
- ✓ Студент існує
- ✓ Email (якщо оновлюється)
- ✓ Телефон (якщо оновлюється)
- ✓ Дата народження (якщо оновлюється)
- ✓ Унікальність student_id_number (якщо оновлюється)

**Можна оновити:** всі поля крім id та enrollment_date

#### 6. Видалення студента

```python
# Видалити студента
deleted = service.delete_student(student_id)

if deleted:
    print("Student deleted successfully")
else:
    print("Delete failed")
```

**Перевірки:**
- ✓ Студент існує

### Довідкові дані

```python
# Отримати список груп
groups = service.get_groups()
for group in groups:
    print(f"- {group['name']} (ID: {group['id']})")

# Отримати список спеціальностей
specialties = service.get_specialties()
for specialty in specialties:
    print(f"- {specialty['name']} ({specialty['code']})")

# Отримати список курсів
courses = service.get_courses()
for course in courses:
    print(f"- Course {course['course_number']}: {course['name']}")
```

### Експорт даних

```python
# Експорт у JSON
count = service.export_to_json('data/students.json')
print(f"Exported {count} students to JSON")

# Експорт у CSV
count = service.export_to_csv('data/students.csv')
print(f"Exported {count} students to CSV")
```

### Статистика

```python
# Отримати статистику
stats = service.get_statistics()

print(f"Total students: {stats['total_students']}")
print(f"Total groups: {stats['total_groups']}")
print(f"Total specialties: {stats['total_specialties']}")

# Студенти по курсам
for course_stat in stats['students_by_course']:
    print(f"Course {course_stat['course_number']}: {course_stat['count']} students")
```

### Допоміжні методи

```python
# Перевірити чи існує студент
if service.student_exists(student_id):
    print("Student exists")

# Перевірити чи доступний номер залікової книжки
if service.student_id_number_available('CS-2024'):
    print("Student ID number is available")
else:
    print("Student ID number is already taken")
```

## Обробка помилок

```python
from src.utils import ValidationError
from psycopg2 import Error as PostgresError

try:
    student_id = service.create_student(data)
    
except ValidationError as e:
    # Помилка валідації даних
    print(f"Invalid data: {e}")
    
except ValueError as e:
    # Порушення бізнес-правил (дублікат, не існує, тощо)
    print(f"Business rule violation: {e}")
    
except PostgresError as e:
    # Помилка бази даних
    print(f"Database error: {e}")
```

## Dependency Injection для тестування

```python
from unittest.mock import Mock
from src.services import StudentService

# Mock repositories
mock_student_repo = Mock()
mock_export_repo = Mock()

# Configure mocks
mock_student_repo.create.return_value = 123
mock_student_repo.exists_by_student_id_number.return_value = False

# Inject mocks
service = StudentService(
    student_repository=mock_student_repo,
    export_repository=mock_export_repo
)

# Test
student_id = service.create_student(valid_data)
assert student_id == 123
mock_student_repo.create.assert_called_once()
```

## Best Practices

1. **Завжди обробляйте помилки** - ValidationError, ValueError, PostgresError
2. **Використовуйте type hints** - сервіс повертає типізовані об'єкти
3. **Не пропускайте валідацію** - сервіс валідує всі дані перед збереженням
4. **Dependency Injection** - для тестування передавайте mock репозиторії
5. **Не обходьте сервіс** - завжди використовуйте сервіс, не репозиторії напряму з API

## Приклад повного циклу

```python
from src.services import StudentService
from src.utils import ValidationError
from datetime import date

service = StudentService()

# 1. Перевірка доступності номера
if not service.student_id_number_available('CS-2024'):
    print("Student ID already exists")
    exit(1)

# 2. Отримання груп для вибору
groups = service.get_groups()
print("Available groups:")
for group in groups:
    print(f"  {group['id']}: {group['name']}")

selected_group_id = groups[0]['id']

# 3. Створення студента
try:
    student_id = service.create_student({
        'last_name': 'Ivanov',
        'first_name': 'Ivan',
        'student_id_number': 'CS-2024',
        'group_id': selected_group_id,
        'email': 'ivanov@example.com',
        'birth_date': date(2001, 5, 15)
    })
    print(f"✓ Student created: {student_id}")
    
except ValidationError as e:
    print(f"✗ Validation error: {e}")
    exit(1)

# 4. Отримання студента
student = service.get_student(student_id)
print(f"✓ Student: {student.get_full_name()}")
print(f"  Group: {student.group_name}")
print(f"  Specialty: {student.specialty_name}")

# 5. Пошук
results, count = service.search_students({'query': 'Ivanov'})
print(f"✓ Found {count} students")

# 6. Експорт
count = service.export_to_json('data/backup.json')
print(f"✓ Exported {count} students")
```

## Тестування

Запустити демо:

```bash
python tests/test_student_service_demo.py
```

Демонстрація показує:
- ✓ Отримання довідкових даних
- ✓ Створення студента
- ✓ Читання студента
- ✓ Список студентів
- ✓ Пошук студентів
- ✓ Оновлення студента
- ✓ Статистика
