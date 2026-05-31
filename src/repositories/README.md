# Repositories Module

Модуль репозиторіїв реалізує **Repository Pattern** для роботи з базою даних PostgreSQL.

## Архітектура

```
┌─────────────────────────────────────┐
│      Service Layer                  │
│  (Business Logic)                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Repository Layer               │
│  (Data Access)                      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  BaseRepository (Abstract)  │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│             ├─► StudentRepository   │
│             └─► ExportRepository    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      DatabaseConnection             │
│  (psycopg2 connection pool)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      PostgreSQL Database            │
│  Schema: s_university               │
└─────────────────────────────────────┘
```

## Компоненти

### 1. DatabaseConnection (`database.py`)

Менеджер підключень до PostgreSQL.

**Особливості:**
- **Singleton pattern** - один екземпляр на додаток
- **Connection pool** - ефективне управління з'єднаннями
- **Context managers** - автоматичне закриття ресурсів
- **RealDictCursor** - результати як словники
- **Автоматичне встановлення search_path** до схеми s_university

**Використання:**

```python
from src.repositories import get_db

db = get_db()

# Execute SELECT query
students = db.execute_query("SELECT * FROM t_students LIMIT 10;")

# Execute SELECT one
student = db.execute_one("SELECT * FROM t_students WHERE id = %s;", (1,))

# Execute INSERT
student_id = db.execute_insert(
    "INSERT INTO t_students (...) VALUES (...) RETURNING id;",
    (...)
)

# Execute UPDATE/DELETE
rows = db.execute_update("UPDATE t_students SET ... WHERE id = %s;", (1,))

# Context manager для cursor
with db.get_cursor() as cur:
    cur.execute("SELECT * FROM t_students;")
    results = cur.fetchall()
```

### 2. BaseRepository (`base_repository.py`)

Абстрактний базовий клас що визначає інтерфейс для всіх репозиторіїв.

**Методи:**
- `create(data)` - створити запис
- `get_by_id(id)` - отримати за ID
- `get_all(offset, limit)` - отримати всі з пагінацією
- `search(params)` - пошук за критеріями
- `update(id, data)` - оновити запис
- `delete(id)` - видалити запис
- `count()` - порахувати кількість
- `exists(id)` - перевірити існування

### 3. StudentRepository (`postgres_repository.py`)

Репозиторій для роботи з таблицею `t_students`.

**Особливості:**
- Використовує VIEW `v_student_full_info` для читання (з JOIN)
- Прямі SQL запити через psycopg2 (без ORM)
- Parameterized queries для захисту від SQL injection
- Динамічне формування WHERE clause для пошуку
- Перевірка унікальності `student_id_number`

**Приклади використання:**

```python
from src.repositories import StudentRepository

repo = StudentRepository()

# Створити студента
student_data = {
    'last_name': 'Shevchenko',
    'first_name': 'Taras',
    'student_id_number': 'CS-2024',
    'group_id': 1,
    'email': 'shevchenko@example.com',
    'birth_date': '2000-01-01'
}
student_id = repo.create(student_data)

# Отримати студента з повною інформацією (VIEW)
student = repo.get_by_id(student_id)
print(student['group_name'])  # З VIEW
print(student['specialty_name'])  # З VIEW

# Отримати всіх студентів
students = repo.get_all(offset=0, limit=50)

# Пошук студентів
results = repo.search({
    'query': 'Shevchenko',  # Пошук по прізвищу/email/групі
    'course_number': 1,
    'limit': 20
})

# Оновити студента
repo.update(student_id, {
    'email': 'new_email@example.com',
    'phone': '+380501234567'
})

# Видалити студента
repo.delete(student_id)

# Перевірити існування
if repo.exists(student_id):
    print("Student exists")

# Перевірити унікальність номера залікової
if repo.exists_by_student_id_number('CS-2024'):
    print("Student ID number already taken")

# Отримати довідкові дані
groups = repo.get_all_groups()
specialties = repo.get_all_specialties()
courses = repo.get_all_courses()
```

**Пошук - підтримувані параметри:**
- `query` - загальний пошук (ILIKE по last_name, email, group_name)
- `group_name` - точний фільтр за групою
- `specialty_code` - фільтр за кодом спеціальності
- `course_number` - фільтр за номером курсу
- `offset`, `limit` - пагінація

### 4. ExportRepository (`export_repository.py`)

Репозиторій для експорту даних у файли.

**Особливості:**
- Експорт у JSON з pretty formatting
- Експорт у CSV з заголовками
- Атомарний запис через тимчасові файли
- Автоматичне перетворення дат у ISO формат
- Підтримка кирилиці (ensure_ascii=False)

**Приклади використання:**

```python
from src.repositories import ExportRepository

repo = ExportRepository()

# Експорт у JSON
count = repo.export_to_json('data/students.json')
print(f"Exported {count} students")

# Експорт у CSV
count = repo.export_to_csv('data/students.csv')
print(f"Exported {count} students")

# Отримати статистику
stats = repo.get_export_stats()
print(f"Total students: {stats['total_students']}")
print(f"Students by course: {stats['students_by_course']}")
```

**Формат JSON:**
```json
{
  "metadata": {
    "total_count": 100,
    "format": "json",
    "version": "1.0"
  },
  "students": [
    {
      "id": 1,
      "last_name": "Shevchenko",
      "first_name": "Taras",
      ...
    }
  ]
}
```

**Формат CSV:**
```csv
id,last_name,first_name,patronymic,student_id_number,email,...
1,Shevchenko,Taras,Hryhorovych,CS-2024,shevchenko@example.com,...
```

## Обробка помилок

Всі репозиторії викидають `psycopg2.Error` при помилках БД:

```python
from psycopg2 import Error as PostgresError

try:
    student_id = repo.create(student_data)
except PostgresError as e:
    print(f"Database error: {e}")
    # Handle error (rollback, retry, etc.)
```

## Connection Pool

DatabaseConnection використовує `SimpleConnectionPool`:
- **Min connections:** 1
- **Max connections:** 10
- Автоматичне управління з'єднаннями
- Повернення з'єднання в pool після використання

## Транзакції

Context managers автоматично обробляють транзакції:
- **commit** - якщо операція успішна
- **rollback** - якщо виникла помилка

```python
with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO t_students ...")
        cur.execute("UPDATE t_groups ...")
        # commit автоматично при виході з context manager
```

## Тестування

Запустити тест підключення:

```bash
python tests/test_database_connection.py
```

Перевіряє:
- ✓ Підключення до БД
- ✓ Наявність схеми s_university
- ✓ Наявність таблиць
- ✓ Наявність VIEW
- ✓ Початкові дані

## Best Practices

1. **Завжди використовуйте parameterized queries** - захист від SQL injection
2. **Використовуйте context managers** - автоматичне закриття ресурсів
3. **Обробляйте PostgresError** - graceful error handling
4. **Не тримайте з'єднання довго** - використовуйте connection pool
5. **Використовуйте VIEW для читання** - готові JOIN'и
6. **Валідуйте дані перед збереженням** - використовуйте validators

## Приклад повного циклу

```python
from src.repositories import StudentRepository
from src.utils import validate_student_data, ValidationError
from psycopg2 import Error as PostgresError
from datetime import date

repo = StudentRepository()

# 1. Валідація даних
try:
    validate_student_data(
        last_name="Ivanov",
        first_name="Ivan",
        student_id_number="CS-2024",
        email="ivanov@example.com",
        birth_date=date(2001, 5, 15)
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    exit(1)

# 2. Перевірка унікальності
if repo.exists_by_student_id_number("CS-2024"):
    print("Student ID already exists")
    exit(1)

# 3. Створення
try:
    student_id = repo.create({
        'last_name': 'Ivanov',
        'first_name': 'Ivan',
        'student_id_number': 'CS-2024',
        'group_id': 1,
        'email': 'ivanov@example.com',
        'birth_date': date(2001, 5, 15)
    })
    print(f"Student created with ID: {student_id}")
except PostgresError as e:
    print(f"Database error: {e}")
    exit(1)

# 4. Читання
student = repo.get_by_id(student_id)
print(f"Student: {student['last_name']} {student['first_name']}")
print(f"Group: {student['group_name']}")
print(f"Specialty: {student['specialty_name']}")
```
