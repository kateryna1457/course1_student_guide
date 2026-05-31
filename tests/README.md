# Тести

Документація по тестуванню проекту Student Directory.

## Структура тестів

```
tests/
├── conftest.py              # Pytest fixtures та конфігурація
├── test_models.py           # Тести OOP моделей
├── test_validators.py       # Тести валідаторів
├── test_repositories.py     # Integration тести репозиторіїв
├── test_services.py         # Тести бізнес-логіки
├── test_api.py              # Тести REST API endpoints
├── test_cli.py              # Тести CLI команд
├── test_seed.py             # Тести генератора даних
└── README.md                # Цей файл
```

## Типи тестів

### Unit тести
Тести окремих компонентів без зовнішніх залежностей:
- `test_models.py` - OOP класи
- `test_validators.py` - функції валідації

### Integration тести
Тести що потребують БД або зовнішніх систем:
- `test_repositories.py` - PostgreSQL репозиторії
- `test_services.py` - сервіси з валідацією
- `test_api.py` - REST API endpoints
- `test_cli.py` - CLI команди
- `test_seed.py` - генератор даних

## Запуск тестів

### Всі тести

```bash
pytest
```

### За маркерами

```bash
# Тільки unit тести (без БД)
pytest -m "not integration"

# Тільки integration тести
pytest -m integration

# Тільки API тести
pytest -m api

# Виключити повільні тести
pytest -m "not slow"
```

### Конкретні файли

```bash
# Один файл
pytest tests/test_models.py

# Один клас
pytest tests/test_models.py::TestStudent

# Один тест
pytest tests/test_models.py::TestStudent::test_student_creation
```

### З покриттям коду

```bash
# Звіт в терміналі
pytest --cov=src --cov-report=term-missing

# HTML звіт
pytest --cov=src --cov-report=html
# Відкрити: htmlcov/index.html
```

### Verbose режим

```bash
# Детальний вивід
pytest -v

# Ще детальніший
pytest -vv

# З виводом print statements
pytest -s
```

## Fixtures

### Database Fixtures

**`test_db_connection`** - Підключення до тестової БД
```python
def test_something(test_db_connection):
    # Використати підключення
    pass
```

**`student_repository`** - StudentRepository instance
```python
def test_repository(student_repository):
    students = student_repository.get_all()
```

**`student_service`** - StudentService instance
```python
def test_service(student_service):
    student_id = student_service.create_student(data)
```

### Data Fixtures

**`sample_student_data`** - Валідні дані студента
```python
def test_create(sample_student_data):
    assert sample_student_data['email'] == 'taras.shevchenko@example.com'
```

**`sample_student_data_minimal`** - Мінімальні обов'язкові поля
**`invalid_student_data`** - Невалідні дані для тестів валідації
**`multiple_students_data`** - Список студентів

### File Fixtures

**`temp_file`** - Тимчасовий файл
**`temp_json_file`** - Тимчасовий JSON файл
**`temp_csv_file`** - Тимчасовий CSV файл

```python
def test_export(temp_json_file):
    export_to_json(temp_json_file)
    assert os.path.exists(temp_json_file)
```

### Cleanup Fixtures

**`cleanup_test_students`** - Автоматичне видалення студентів після тесту
```python
def test_create(student_repository, cleanup_test_students):
    student_id = student_repository.create(data)
    cleanup_test_students(student_id)  # Буде видалено після тесту
```

### API Fixtures

**`api_client`** - FastAPI TestClient
```python
def test_endpoint(api_client):
    response = api_client.get("/api/students/")
    assert response.status_code == 200
```

## Приклади тестів

### Unit тест моделі

```python
def test_student_creation():
    student = Student(
        id=1,
        last_name="Shevchenko",
        first_name="Taras",
        email="taras@example.com",
        birth_date=date(2005, 3, 9)
    )
    
    assert student.id == 1
    assert student.get_full_name() == "Shevchenko Taras"
```

### Integration тест репозиторію

```python
@pytest.mark.integration
def test_create_student(student_repository, sample_student_data, cleanup_test_students):
    student_id = student_repository.create(sample_student_data)
    cleanup_test_students(student_id)
    
    assert student_id > 0
    
    student = student_repository.get_by_id(student_id)
    assert student is not None
```

### API тест

```python
@pytest.mark.api
def test_get_students(api_client):
    response = api_client.get("/api/students/")
    
    assert response.status_code == 200
    data = response.json()
    assert 'students' in data
```

### CLI тест

```python
def test_list_command():
    from typer.testing import CliRunner
    from src.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["list", "--limit", "5"])
    
    assert result.exit_code == 0
```

## Markers

Використовуйте markers для категоризації тестів:

```python
@pytest.mark.integration
def test_database_operation():
    pass

@pytest.mark.slow
def test_long_running():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass
```

## Покриття коду

### Мета покриття

- **Загальне покриття**: ≥80%
- **Критичні модулі** (validators, services): ≥90%
- **Моделі та утиліти**: ≥85%

### Перевірка покриття

```bash
# Згенерувати звіт
pytest --cov=src --cov-report=html

# Відкрити HTML звіт
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Виключення з покриття

Деякі рядки можна виключити:

```python
def some_function():
    if DEBUG:  # pragma: no cover
        print("Debug info")
```

## CI/CD Integration

### GitHub Actions приклад

```yaml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Помилка: "Database connection failed"

**Рішення:**
1. Переконатися що PostgreSQL запущений: `docker-compose up -d postgres`
2. Перевірити змінні середовища в `.env`
3. Запустити init.sql: `docker-compose restart postgres`

### Помилка: "No groups available"

**Рішення:**
```bash
# Перезапустити БД з ініціалізацією
docker-compose down -v
docker-compose up -d postgres
# Почекати 5 секунд для ініціалізації
```

### Тести падають випадково

**Можливі причини:**
1. **Race conditions** - тести змінюють спільні дані
2. **Cleanup не спрацював** - використовуйте `cleanup_test_students` fixture
3. **Тестова БД не ізольована** - кожен тест має бути незалежним

**Рішення:**
- Використовуйте fixtures для cleanup
- Генеруйте унікальні дані (timestamp, UUID)
- Використовуйте транзакції (якщо потрібно)

### Slow tests

**Оптимізація:**
1. Позначити повільні тести `@pytest.mark.slow`
2. Запускати окремо: `pytest -m "not slow"`
3. Використовувати `pytest-xdist` для паралелізації:
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

## Best Practices

### 1. Незалежність тестів
Кожен тест має бути незалежним:
```python
# ✅ Good
def test_create(cleanup_test_students):
    student_id = create_student(data)
    cleanup_test_students(student_id)

# ❌ Bad - залежить від іншого тесту
def test_update():
    update_student(1)  # Припускає що студент з ID 1 існує
```

### 2. Описові назви
```python
# ✅ Good
def test_create_student_with_invalid_email_raises_validation_error():
    pass

# ❌ Bad
def test_create():
    pass
```

### 3. Arrange-Act-Assert
```python
def test_create_student():
    # Arrange
    data = {'name': 'Test', 'email': 'test@example.com'}
    
    # Act
    student_id = service.create_student(data)
    
    # Assert
    assert student_id > 0
```

### 4. Використання fixtures
```python
# ✅ Good
def test_something(sample_student_data):
    result = process(sample_student_data)

# ❌ Bad - дублювання даних
def test_something():
    data = {'name': 'Test', 'email': '...'}  # Дублюється в кожному тесті
```

### 5. Перевірка помилок
```python
# Перевірити що викидається помилка
with pytest.raises(ValidationError, match="Invalid email"):
    validate_email("not-an-email")
```

## Статистика тестів

Після запуску всіх тестів:
```
tests/test_models.py ........          [ 12%]
tests/test_validators.py ............. [ 35%]
tests/test_repositories.py ........... [ 58%]
tests/test_services.py ............... [ 78%]
tests/test_api.py .................... [ 92%]
tests/test_cli.py ....                 [ 98%]
tests/test_seed.py ..                  [100%]

========== 85 passed in 12.34s ==========

Coverage: 87%
```

## Додаткові ресурси

- [Pytest документація](https://docs.pytest.org/)
- [Pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
