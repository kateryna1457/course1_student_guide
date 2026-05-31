# Студенти курсу

Простий довідник для управління даними про студентів курсу з REST API та CLI інтерфейсами.

## Про проект

**Курсова робота 1-го курсу**  
**Виконавець:** Алексєєва Катерина Павлівна  
**Група:** ЗІПЗ-25-1-ict

## Опис

Програма реалізує повнофункціональний довідник, що зберігає дані про студентів курсу, з підтримкою двох інтерфейсів:
- **REST API** - для інтеграції з веб-додатками
- **CLI (Command Line Interface)** - для роботи через термінал

## Функціональність

Програма забезпечує наступні можливості:

- ✅ **Введення нових даних** із перевіркою їх коректності (валідація email, телефону, дат)
- ✅ **Перегляд довідника** з усіма записами та пагінацією
- ✅ **Пошук необхідних даних** за прізвищем, email, групою, спеціальністю, курсом
- ✅ **Коригування даних** існуючих записів
- ✅ **Видалення непотрібних записів**
- ✅ **Збереження даних у файлі** (PostgreSQL база даних)
- ✅ **Експорт даних** у форматах JSON та CSV
- ✅ **Статистика** по студентам, групам та спеціальностям

## Технології

### Backend
- **Python 3.11+** - основна мова програмування
- **FastAPI** - сучасний веб-фреймворк для REST API
- **Typer** - фреймворк для CLI додатків
- **Rich** - бібліотека для красивого виводу в термінал
- **Pydantic** - валідація даних
- **psycopg2** - драйвер для PostgreSQL

### База даних
- **PostgreSQL 16** - реляційна база даних
- **Docker** - контейнеризація БД

### Інструменти розробки
- **pytest** - фреймворк для тестування
- **Docker Compose** - оркестрація контейнерів
- **Uvicorn** - ASGI сервер

## Встановлення та запуск

### Передумови
- Python 3.11 або вище
- Docker та Docker Compose
- Git

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd "семестр 2\Курсова робота"
```

### 2. Налаштування середовища
```bash
# Створити віртуальне середовище
python -m venv .venv

# Активувати (Windows)
.venv\Scripts\activate

# Активувати (Linux/Mac)
source .venv/bin/activate

# Встановити залежності
pip install -e .
```

### 3. Налаштування бази даних
```bash
# Скопіювати приклад конфігурації
cp .env.example .env

# Запустити PostgreSQL в Docker (з папки docker)
cd docker
docker-compose up -d postgres
cd ..
```

### 4. Запуск додатку

#### API сервер
```bash
# Запуск через Python
python -m src.main

# Або через Docker Compose (повний стек)
cd docker
docker-compose up
```

API буде доступний за адресою: `http://localhost:8000`  
Документація API (Swagger): `http://localhost:8000/docs`

#### CLI інтерфейс
```bash
# Показати допомогу
python -m src.cli --help

# Заповнити БД тестовими даними
python -m src.cli seed --count 50

# Переглянути список студентів
python -m src.cli list

# Інші команди див. у розділі "Використання CLI"
```

## Структура проекту

```
├── docker/                      # Docker конфігурації
│   ├── Dockerfile              # Dockerfile для backend
│   ├── docker-compose.yml      # Docker Compose конфігурація
│   └── postgres/               # PostgreSQL конфігурації та SQL скрипти
│       ├── schemas/ddl/        # DDL для створення схеми БД
│       ├── tables/ddl/         # DDL для створення таблиць
│       ├── tables/dml/         # DML для початкового заповнення
│       ├── views/ddl/          # DDL для створення представлень
│       └── init-db.sql         # Головний скрипт ініціалізації
│
├── src/                        # Вихідний код програми
│   ├── api/                    # REST API
│   │   ├── routes/            # Маршрути API (endpoints)
│   │   ├── main.py            # FastAPI додаток
│   │   └── exceptions.py      # Обробники помилок
│   │
│   ├── models/                 # Моделі даних
│   │   ├── student.py         # Модель студента
│   │   ├── group.py           # Модель групи
│   │   ├── course.py          # Модель курсу
│   │   ├── specialty.py       # Модель спеціальності
│   │   └── schemas.py         # Pydantic схеми для валідації
│   │
│   ├── repositories/           # Шар доступу до даних
│   │   ├── base_repository.py       # Базовий репозиторій
│   │   ├── postgres_repository.py   # PostgreSQL репозиторій
│   │   └── export_repository.py     # Експорт даних
│   │
│   ├── services/               # Бізнес-логіка
│   │   └── student_service.py # Сервіс роботи зі студентами
│   │
│   ├── utils/                  # Допоміжні функції
│   │   ├── validators.py      # Валідатори
│   │   └── seed.py            # Генерація тестових даних
│   │
│   ├── cli.py                  # CLI інтерфейс (Typer)
│   ├── main.py                 # Точка входу для API
│   ├── config.py               # Конфігурація додатку
│   └── constants.py            # Константи
│
├── tests/                      # Тести
│   ├── test_models.py         # Тести моделей
│   ├── test_services.py       # Тести сервісів
│   ├── test_api.py            # Тести API endpoints
│   └── test_cli.py            # Тести CLI команд
│
├── docs/                       # Документація
│   ├── task.txt               # Завдання курсової роботи
│   ├── CONFIGURATION.md       # Інструкції з налаштування
│   └── SEED_DATA.md           # Документація по тестовим даним
│
├── .env.example                # Приклад конфігурації середовища
├── pyproject.toml             # Конфігурація проекту та залежності
├── pytest.ini                 # Конфігурація pytest
└── README.md                  # Цей файл
```

## Використання

### CLI команди

#### Перегляд студентів
```bash
# Список всіх студентів (з пагінацією)
python -m src.cli list --limit 20 --offset 0

# Детальна інформація про студента
python -m src.cli show CS-2024
```

#### Додавання студента
```bash
# Інтерактивне додавання
python -m src.cli add
```

Приклад взаємодії:
```
Додати нового студента

Доступні групи:
  1: ЗІПЗ-25-1
  2: ЗІПЗ-25-2

Прізвище: Іванов
Ім'я: Іван
По батькові: Іванович
Номер залікової книжки (наприклад, CS-2024): CS-2024-001
ID групи: 1
Email: ivanov@example.com
Телефон (опціонально): +380501234567
Дата народження (YYYY-MM-DD, наприклад 2000-01-15): 2005-05-15

Створити студента з цими даними? [y/n]: y

✓ Студента створено! ID: 123
```

#### Пошук студентів
```bash
# Пошук за прізвищем
python -m src.cli search "Іванов"

# Пошук за групою
python -m src.cli search --group "ЗІПЗ-25-1"

# Пошук за курсом
python -m src.cli search --course 1

# Комбінований пошук
python -m src.cli search "Петров" --group "ЗІПЗ-25-2" --course 1

# Пошук за спеціальністю
python -m src.cli search --specialty "122"
```

#### Оновлення даних
```bash
# Інтерактивне оновлення
python -m src.cli update CS-2024-001
```

#### Видалення студента
```bash
# Видалення з підтвердженням
python -m src.cli delete CS-2024-001
```

#### Експорт даних
```bash
# Експорт всіх студентів у JSON
python -m src.cli export json

# Експорт студентів у CSV
python -m src.cli export csv

# Експорт з фільтрацією
python -m src.cli export json --group "ЗІПЗ-25-1"
python -m src.cli export csv --course 1 --specialty "122"
```

#### Довідкова інформація
```bash
# Список груп
python -m src.cli groups

# Список спеціальностей
python -m src.cli specialties

# Статистика
python -m src.cli stats
```

#### Заповнення тестовими даними
```bash
# Створити 20 випадкових студентів (за замовчуванням)
python -m src.cli seed

# Створити 100 студентів
python -m src.cli seed --count 100
```

### REST API приклади

#### Отримання списку студентів
```bash
curl http://localhost:8000/api/students?limit=10&offset=0
```

#### Отримання студента за ID
```bash
curl http://localhost:8000/api/students/123
```

#### Створення нового студента
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "last_name": "Іванов",
    "first_name": "Іван",
    "patronymic": "Іванович",
    "student_id_number": "CS-2024-001",
    "group_id": 1,
    "email": "ivanov@example.com",
    "phone": "+380501234567",
    "birth_date": "2005-05-15"
  }'
```

#### Пошук студентів
```bash
# Пошук за запитом
curl "http://localhost:8000/api/students/search?query=Іванов"

# Пошук за групою
curl "http://localhost:8000/api/students/search?group_name=ЗІПЗ-25-1"

# Комбінований пошук
curl "http://localhost:8000/api/students/search?query=Петров&course_number=1"
```

#### Оновлення студента
```bash
curl -X PUT http://localhost:8000/api/students/123 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new.email@example.com",
    "phone": "+380509876543"
  }'
```

#### Видалення студента
```bash
curl -X DELETE http://localhost:8000/api/students/123
```

#### Статистика
```bash
curl http://localhost:8000/api/reference/statistics
```

### Swagger документація

Повна інтерактивна документація API доступна за адресою:
```
http://localhost:8000/docs
```

Альтернативна документація (ReDoc):
```
http://localhost:8000/redoc
```
