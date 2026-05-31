# Docker Configuration

Ця папка містить всі Docker-конфігурації для проекту.

## Структура

```
docker/
├── Dockerfile              # Docker образ для backend застосунку
├── docker-compose.yml      # Оркестрація сервісів (PostgreSQL + Backend)
└── postgres/               # PostgreSQL конфігурації
    ├── init-db.sql         # Головний скрипт ініціалізації БД
    ├── schemas/ddl/        # DDL скрипти для створення схем
    ├── tables/ddl/         # DDL скрипти для створення таблиць
    ├── tables/dml/         # DML скрипти для початкових даних
    └── views/ddl/          # DDL скрипти для створення представлень
```

## Використання

### Запуск всіх сервісів

```bash
cd docker
docker-compose up
```

Це запустить:
- PostgreSQL на порті 5432
- Backend API на порті 8000

### Запуск тільки PostgreSQL

```bash
cd docker
docker-compose up -d postgres
```

### Зупинка сервісів

```bash
cd docker
docker-compose down
```

### Видалення даних (скидання БД)

```bash
cd docker
docker-compose down -v
```

## Налаштування

Конфігурація через файл `.env` в кореневій папці проекту. Використовуйте `.env.example` як шаблон.

### Основні змінні

- `POSTGRES_USER` - ім'я користувача БД
- `POSTGRES_PASSWORD` - пароль БД
- `POSTGRES_DB` - ім'я бази даних
- `DATABASE_SCHEMA` - схема БД (за замовчуванням: s_university)
- `API_PORT` - порт для API (за замовчуванням: 8000)

## Ініціалізація БД

При першому запуску PostgreSQL автоматично виконує скрипти з папки `postgres/`:
1. Створює схему БД
2. Створює таблиці (курси, спеціальності, групи, студенти)
3. Заповнює довідкові дані (курси, спеціальності, тестові групи)
4. Створює представлення (v_student_full_info)

## Доступ до БД

### З хосту

```bash
psql -h localhost -U student_user -d students_db
```

### З Docker контейнера

```bash
docker exec -it students_db psql -U student_user -d students_db
```

## Відлагодження

### Переглянути логи PostgreSQL

```bash
docker-compose logs postgres
```

### Переглянути логи Backend

```bash
docker-compose logs backend
```

### Перезапустити сервіс

```bash
docker-compose restart backend
# або
docker-compose restart postgres
```
