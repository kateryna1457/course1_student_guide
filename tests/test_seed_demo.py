"""
Демо-скрипт для тестування генератора тестових даних.

Запуск: python tests/test_seed_demo.py
"""

import sys
from pathlib import Path

# Додати src до Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.seed import DataGenerator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_generate_student_id_number():
    """Тест генерації номера залікової книжки."""
    console.print("\n[bold cyan]Тест 1: Генерація номера залікової книжки[/bold cyan]\n")

    generator = DataGenerator()

    examples = [
        ("CS-11", 2024),
        ("IT-23", 2023),
        ("SE-15", 2025),
    ]

    table = Table(title="Приклади номерів залікових книжок")
    table.add_column("Група", style="cyan")
    table.add_column("Рік", style="yellow")
    table.add_column("Номер залікової", style="green")

    for group_name, year in examples:
        student_id = generator.generate_student_id_number(group_name, year)
        table.add_row(group_name, str(year), student_id)

    console.print(table)


def test_generate_phone_number():
    """Тест генерації телефонного номера."""
    console.print("\n[bold cyan]Тест 2: Генерація номера телефону[/bold cyan]\n")

    generator = DataGenerator()

    table = Table(title="Приклади українських номерів")
    table.add_column("#", style="dim")
    table.add_column("Номер телефону", style="green")

    for i in range(10):
        phone = generator.generate_phone_number()
        table.add_row(str(i + 1), phone)

    console.print(table)


def test_generate_birth_date():
    """Тест генерації дати народження."""
    console.print("\n[bold cyan]Тест 3: Генерація дати народження[/bold cyan]\n")

    generator = DataGenerator()

    table = Table(title="Приклади дат народження")
    table.add_column("#", style="dim")
    table.add_column("Дата народження", style="green")
    table.add_column("Вік (років)", style="yellow")

    from datetime import date
    today = date.today()

    for i in range(10):
        birth_date = generator.generate_birth_date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1

        table.add_row(str(i + 1), str(birth_date), str(age))

    console.print(table)


def test_generate_student():
    """Тест генерації повних даних студента."""
    console.print("\n[bold cyan]Тест 4: Генерація повних даних студента[/bold cyan]\n")

    generator = DataGenerator()

    # Приклад групи
    example_group = {
        'id': 1,
        'name': 'CS-11',
        'admission_year': 2024
    }

    # Згенерувати 3 студентів
    for i in range(3):
        student = generator.generate_student(example_group)

        info_text = f"""
[cyan]Особиста інформація:[/cyan]
  [green]Прізвище:[/green] {student['last_name']}
  [green]Ім'я:[/green] {student['first_name']}
  [green]По батькові:[/green] {student['patronymic']}
  [green]Залікова книжка:[/green] {student['student_id_number']}
  [green]Email:[/green] {student['email']}
  [green]Телефон:[/green] {student['phone'] or 'не вказано'}

[cyan]Дати:[/cyan]
  [yellow]Дата народження:[/yellow] {student['birth_date']}
  [yellow]Дата зарахування:[/yellow] {student['enrollment_date']}

[cyan]Група:[/cyan]
  [magenta]ID групи:[/magenta] {student['group_id']}
"""

        console.print(Panel(info_text, title=f"Студент #{i + 1}", border_style="green"))


def test_data_quality():
    """Тест якості даних (валідація)."""
    console.print("\n[bold cyan]Тест 5: Перевірка якості даних[/bold cyan]\n")

    from src.utils import (
        validate_student_id_number,
        validate_email,
        validate_phone,
        validate_birth_date,
        ValidationError
    )

    generator = DataGenerator()

    example_group = {
        'id': 1,
        'name': 'CS-11',
        'admission_year': 2024
    }

    # Згенерувати 20 студентів і перевірити валідність
    results = {
        'total': 0,
        'valid_student_id': 0,
        'valid_email': 0,
        'valid_phone': 0,
        'valid_birth_date': 0,
        'all_valid': 0
    }

    for _ in range(20):
        student = generator.generate_student(example_group)
        results['total'] += 1

        # Перевірити кожне поле
        try:
            validate_student_id_number(student['student_id_number'])
            results['valid_student_id'] += 1
        except ValidationError:
            pass

        try:
            validate_email(student['email'])
            results['valid_email'] += 1
        except ValidationError:
            pass

        if student['phone']:
            try:
                validate_phone(student['phone'])
                results['valid_phone'] += 1
            except ValidationError:
                pass
        else:
            results['valid_phone'] += 1  # None is valid

        try:
            validate_birth_date(student['birth_date'])
            results['valid_birth_date'] += 1
        except ValidationError:
            pass

        # Перевірити чи всі поля валідні
        if (results['valid_student_id'] == results['total'] and
            results['valid_email'] == results['total'] and
            results['valid_phone'] == results['total'] and
            results['valid_birth_date'] == results['total']):
            results['all_valid'] = results['total']

    # Вивести результати
    table = Table(title="Результати перевірки валідності")
    table.add_column("Поле", style="cyan")
    table.add_column("Валідних", style="green")
    table.add_column("Всього", style="yellow")
    table.add_column("%", style="magenta")

    for field, valid_count in [
        ("Номер залікової", results['valid_student_id']),
        ("Email", results['valid_email']),
        ("Телефон", results['valid_phone']),
        ("Дата народження", results['valid_birth_date']),
    ]:
        percentage = (valid_count / results['total']) * 100
        table.add_row(
            field,
            str(valid_count),
            str(results['total']),
            f"{percentage:.1f}%"
        )

    console.print(table)

    if results['all_valid'] == results['total']:
        console.print("\n[green]✓ Всі згенеровані дані валідні![/green]")
    else:
        console.print(f"\n[red]✗ {results['total'] - results['all_valid']} записів з помилками[/red]")


if __name__ == "__main__":
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   Тестування генератора даних (Seed) [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    try:
        test_generate_student_id_number()
        test_generate_phone_number()
        test_generate_birth_date()
        test_generate_student()
        test_data_quality()

        console.print("\n[bold green]✓ Всі тести пройдено успішно![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Помилка: {e}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
