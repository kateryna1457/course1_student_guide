"""
CLI інтерфейс для роботи з довідником студентів.

Використовує Typer для CLI та Rich для красивого виводу.
"""

import typer
from typing import Optional
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.services import StudentService
from src.utils import ValidationError

# Створити CLI додаток
app = typer.Typer(
    name="students",
    help="Довідник студентів курсу - CLI інтерфейс",
    add_completion=False
)

# Rich console
console = Console()

# Ініціалізувати сервіс
service = StudentService()


@app.command()
def add():
    """
    Додати нового студента (інтерактивно).

    Запитує всі необхідні дані через інтерактивні промпти.
    """
    console.print("\n[bold cyan]Додати нового студента[/bold cyan]\n")

    try:
        # Get groups for selection
        groups = service.get_groups()
        if not groups:
            console.print("[red]✗ Немає доступних груп! Запустіть seed команду спочатку.[/red]")
            raise typer.Exit(1)

        # Show groups
        console.print("[yellow]Доступні групи:[/yellow]")
        for group in groups[:10]:  # Show first 10
            console.print(f"  {group['id']}: {group['name']}")

        # Collect data
        last_name = Prompt.ask("Прізвище")
        first_name = Prompt.ask("Ім'я")
        patronymic = Prompt.ask("По батькові", default="")
        student_id_number = Prompt.ask("Номер залікової книжки (наприклад, CS-2024)")

        group_id_str = Prompt.ask("ID групи")
        group_id = int(group_id_str)

        email = Prompt.ask("Email")
        phone = Prompt.ask("Телефон (опціонально)", default="")

        birth_date_str = Prompt.ask("Дата народження (YYYY-MM-DD, наприклад 2000-01-15)")
        birth_date = date.fromisoformat(birth_date_str)

        # Confirm
        if not Confirm.ask("\nСтворити студента з цими даними?"):
            console.print("[yellow]Скасовано[/yellow]")
            return

        # Create student
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Створення студента...", total=None)

            student_data = {
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic or None,
                'student_id_number': student_id_number,
                'group_id': group_id,
                'email': email,
                'phone': phone or None,
                'birth_date': birth_date
            }

            student_id = service.create_student(student_data)

        console.print(f"\n[green]✓ Студента створено! ID: {student_id}[/green]")

        # Show created student
        student = service.get_student(student_id)
        _show_student_details(student)

    except ValueError as e:
        console.print(f"\n[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)
    except ValidationError as e:
        console.print(f"\n[red]✗ Невалідні дані: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Несподівана помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    offset: int = typer.Option(0, help="Зміщення"),
    limit: int = typer.Option(20, help="Кількість записів")
):
    """
    Показати список студентів.

    Виводить таблицю зі студентами з пагінацією.
    """
    try:
        students, total = service.list_students(offset=offset, limit=limit)

        if not students:
            console.print("[yellow]Студентів не знайдено[/yellow]")
            return

        # Create table
        table = Table(title=f"Список студентів ({offset + 1}-{offset + len(students)} з {total})")

        table.add_column("ID", style="cyan", width=6)
        table.add_column("Прізвище Ім'я", style="green", width=30)
        table.add_column("Залікова", style="yellow", width=15)
        table.add_column("Група", style="magenta", width=10)
        table.add_column("Курс", style="blue", width=6)
        table.add_column("Email", style="white", width=30)

        for student in students:
            table.add_row(
                str(student.id),
                student.get_full_name(),
                student.student_id_number,
                student.group_name,
                str(student.course_number),
                student.email
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Всього: {total} студентів[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def show(
    student_id_number: str = typer.Argument(..., help="Номер залікової книжки студента (наприклад: CS-2024)")
):
    """
    Показати детальну інформацію про студента.

    Приклади:
        python -m src.cli show CS-2024
        python -m src.cli show SE-2024
    """
    try:
        student = service.get_student_by_id_number(student_id_number)

        if not student:
            console.print(f"[red]✗ Студента з номером {student_id_number} не знайдено[/red]")
            raise typer.Exit(1)

        _show_student_details(student)

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    query: Optional[str] = typer.Argument(None, help="Пошуковий запит (прізвище, email, група)"),
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Фільтр за назвою групи"),
    specialty: Optional[str] = typer.Option(None, "--specialty", "-s", help="Фільтр за кодом спеціальності"),
    course: Optional[int] = typer.Option(None, "--course", "-c", help="Фільтр за номером курсу (1-6)"),
    offset: int = typer.Option(0, "--offset", help="Зміщення для пагінації"),
    limit: int = typer.Option(50, "--limit", help="Кількість записів (макс 100)")
):
    """
    Пошук студентів за критеріями.

    Можна використовувати загальний пошук та/або фільтри.

    Приклади:
        python -m src.cli search "Іванов"
        python -m src.cli search --group "IT-11"
        python -m src.cli search --course 1
        python -m src.cli search "Петров" --group "CS-11"
        python -m src.cli search --specialty "122" --course 1
    """
    try:
        # Build search parameters
        search_params = {
            'offset': offset,
            'limit': min(limit, 100)  # Max 100
        }

        if query:
            search_params['query'] = query
        if group:
            search_params['group_name'] = group
        if specialty:
            search_params['specialty_code'] = specialty
        if course:
            search_params['course_number'] = course

        # Show search criteria
        if query or group or specialty or course:
            console.print("[cyan]Критерії пошуку:[/cyan]")
            if query:
                console.print(f"  • Запит: {query}")
            if group:
                console.print(f"  • Група: {group}")
            if specialty:
                console.print(f"  • Спеціальність: {specialty}")
            if course:
                console.print(f"  • Курс: {course}")
            console.print()

        students, count = service.search_students(search_params)

        if not students:
            console.print("[yellow]Нічого не знайдено[/yellow]")
            return

        # Create table
        title_parts = []
        if query:
            title_parts.append(f"'{query}'")
        if group:
            title_parts.append(f"група {group}")
        if specialty:
            title_parts.append(f"спец. {specialty}")
        if course:
            title_parts.append(f"курс {course}")

        title = "Результати пошуку: " + ", ".join(title_parts) if title_parts else "Усі студенти"
        title += f" ({count} знайдено)"

        table = Table(title=title)

        table.add_column("ID", style="cyan", width=6)
        table.add_column("Прізвище Ім'я", style="green", width=30)
        table.add_column("Залікова", style="yellow", width=15)
        table.add_column("Група", style="magenta", width=10)
        table.add_column("Email", style="white", width=30)

        for student in students:
            table.add_row(
                str(student.id),
                student.get_full_name(),
                student.student_id_number,
                student.group_name,
                student.email
            )

        console.print("\n")
        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    student_id_number: str = typer.Argument(..., help="Номер залікової книжки студента (наприклад: CS-2024)")
):
    """
    Оновити дані студента (інтерактивно).

    Приклади:
        python -m src.cli update CS-2024
        python -m src.cli update SE-2024
    """
    try:
        # Check if student exists
        student = service.get_student_by_id_number(student_id_number)
        if not student:
            console.print(f"[red]✗ Студента з номером {student_id_number} не знайдено[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold cyan]Оновити студента {student_id_number}[/bold cyan]\n")
        _show_student_details(student)

        console.print("\n[yellow]Введіть нові значення (Enter щоб пропустити):[/yellow]\n")

        # Collect updates
        updates = {}

        email = Prompt.ask("Email", default=student.email)
        if email != student.email:
            updates['email'] = email

        phone = Prompt.ask("Телефон", default=student.phone or "")
        if phone and phone != (student.phone or ""):
            updates['phone'] = phone

        if not updates:
            console.print("[yellow]Нічого не змінено[/yellow]")
            return

        # Confirm
        if not Confirm.ask("\nОновити студента?"):
            console.print("[yellow]Скасовано[/yellow]")
            return

        # Update
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Оновлення...", total=None)
            service.update_student_by_id_number(student_id_number, updates)

        console.print("\n[green]✓ Студента оновлено![/green]")

        # Show updated student
        student = service.get_student_by_id_number(student_id_number)
        _show_student_details(student)

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    student_id_number: str = typer.Argument(..., help="Номер залікової книжки студента (наприклад: CS-2024)")
):
    """
    Видалити студента.

    Приклади:
        python -m src.cli delete CS-2024
        python -m src.cli delete SE-2024
    """
    try:
        # Check if student exists
        student = service.get_student_by_id_number(student_id_number)
        if not student:
            console.print(f"[red]✗ Студента з номером {student_id_number} не знайдено[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold red]Видалити студента {student_id_number}?[/bold red]\n")
        _show_student_details(student)

        if not Confirm.ask("\n[red]Підтвердити видалення?[/red]"):
            console.print("[yellow]Скасовано[/yellow]")
            return

        # Delete
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Видалення...", total=None)
            service.delete_student_by_id_number(student_id_number)

        console.print(f"\n[green]✓ Студента {student.get_full_name()} видалено[/green]")

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def export(
    format: str = typer.Argument(..., help="Формат: json або csv"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Пошуковий запит (прізвище, email, група)"),
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Фільтр за назвою групи"),
    specialty: Optional[str] = typer.Option(None, "--specialty", "-s", help="Фільтр за кодом спеціальності"),
    course: Optional[int] = typer.Option(None, "--course", "-c", help="Фільтр за номером курсу (1-6)")
):
    """
    Експортувати студентів у файл з можливістю фільтрації.

    Файл буде збережено у demo/exports/students_[timestamp].json або .csv

    Приклади:
        python -m src.cli export json
        python -m src.cli export csv
        python -m src.cli export json --group "CS-11"
        python -m src.cli export csv --course 1
        python -m src.cli export json --query "Іванов" --group "CS-11"
    """
    import os
    from datetime import datetime
    from pathlib import Path

    try:
        # Validate format
        if format.lower() not in ["json", "csv"]:
            console.print(f"[red]✗ Непідтримуваний формат: {format}[/red]")
            console.print("[yellow]Використовуйте: json або csv[/yellow]")
            raise typer.Exit(1)

        # Validate course number
        if course is not None and (course < 1 or course > 6):
            console.print(f"[red]✗ Номер курсу має бути від 1 до 6[/red]")
            raise typer.Exit(1)

        # Build search parameters
        search_params = {}
        if query:
            search_params['query'] = query
        if group:
            search_params['group_name'] = group
        if specialty:
            search_params['specialty_code'] = specialty
        if course:
            search_params['course_number'] = course

        # Show filters if any
        if search_params:
            console.print("[cyan]Фільтри:[/cyan]")
            if query:
                console.print(f"  • Пошук: {query}")
            if group:
                console.print(f"  • Група: {group}")
            if specialty:
                console.print(f"  • Спеціальність: {specialty}")
            if course:
                console.print(f"  • Курс: {course}")
            console.print()

        # Create demo/exports directory
        export_dir = Path("demo/exports")
        export_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"students_{timestamp}.{format.lower()}"
        file_path = export_dir / filename

        console.print(f"[cyan]Експорт у {file_path}...[/cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(f"Експорт у {format.upper()}...", total=None)

            if format.lower() == "json":
                count = service.export_to_json(str(file_path), search_params=search_params if search_params else None)
            else:  # csv
                count = service.export_to_csv(str(file_path), search_params=search_params if search_params else None)

        # Get file size
        file_size = os.path.getsize(file_path)
        size_kb = file_size / 1024

        console.print(f"\n[green]✓ Експорт завершено![/green]")
        console.print(f"[dim]Файл:[/dim] {file_path}")
        console.print(f"[dim]Експортовано:[/dim] {count} студентів")
        console.print(f"[dim]Розмір:[/dim] {size_kb:.1f} KB")

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def groups():
    """Показати список всіх груп."""
    try:
        groups_list = service.get_groups()

        if not groups_list:
            console.print("[yellow]Груп не знайдено[/yellow]")
            return

        # Create table
        table = Table(title="Список груп")

        table.add_column("ID", style="cyan", width=6)
        table.add_column("Назва", style="green", width=15)
        table.add_column("Рік вступу", style="yellow", width=15)

        for group in groups_list:
            table.add_row(
                str(group['id']),
                group['name'],
                str(group['admission_year'])
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Всього: {len(groups_list)} груп[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def specialties():
    """Показати список всіх спеціальностей."""
    try:
        specialties_list = service.get_specialties()

        if not specialties_list:
            console.print("[yellow]Спеціальностей не знайдено[/yellow]")
            return

        # Create table
        table = Table(title="Список спеціальностей")

        table.add_column("ID", style="cyan", width=6)
        table.add_column("Назва", style="green", width=40)
        table.add_column("Код", style="yellow", width=10)

        for specialty in specialties_list:
            table.add_row(
                str(specialty['id']),
                specialty['name'],
                specialty['code'] or ""
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Всього: {len(specialties_list)} спеціальностей[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def stats():
    """Показати статистику."""
    try:
        statistics = service.get_statistics()

        # Create panel with stats
        stats_text = f"""
[cyan]Загальна статистика:[/cyan]

  [green]Студентів:[/green] {statistics['total_students']}
  [green]Груп:[/green] {statistics['total_groups']}
  [green]Спеціальностей:[/green] {statistics['total_specialties']}
"""

        if statistics.get('students_by_course'):
            stats_text += "\n[cyan]Студентів по курсам:[/cyan]\n"
            for course_stat in statistics['students_by_course']:
                stats_text += f"  [yellow]Курс {course_stat['course_number']}:[/yellow] {course_stat['count']} студентів\n"

        console.print(Panel(stats_text, title="📊 Статистика", border_style="blue"))

    except Exception as e:
        console.print(f"[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def seed(count: int = typer.Option(20, help="Кількість студентів для генерації")):
    """
    Заповнити БД тестовими даними.

    Генерує випадкових студентів з реалістичними українськими ПІБ.
    """
    try:
        console.print(f"\n[bold cyan]Генерація {count} студентів...[/bold cyan]\n")

        # Підтвердження
        if not Confirm.ask(f"Створити {count} випадкових студентів?"):
            console.print("[yellow]Скасовано[/yellow]")
            return

        # Імпортувати seed функцію
        from src.utils.seed import seed_database

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Генерація студентів...", total=None)

            created_count = seed_database(count)

            progress.update(task, completed=True)

        console.print(f"\n[green]✓ Створено {created_count} студентів![/green]")

        # Показати статистику
        statistics = service.get_statistics()
        console.print(f"\n[cyan]Всього в БД:[/cyan] {statistics['total_students']} студентів")

    except ValueError as e:
        console.print(f"\n[red]✗ Помилка: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Несподівана помилка: {e}[/red]")
        raise typer.Exit(1)


def _show_student_details(student):
    """
    Показати детальну інформацію про студента.

    Args:
        student: StudentFullInfo об'єкт
    """
    info_text = f"""
[cyan]Особиста інформація:[/cyan]
  [green]ПІБ:[/green] {student.get_full_name()}
  [green]Залікова книжка:[/green] {student.student_id_number}
  [green]Email:[/green] {student.email}
  [green]Телефон:[/green] {student.phone or 'не вказано'}
  [green]Дата народження:[/green] {student.birth_date}
  [green]Дата зарахування:[/green] {student.enrollment_date}

[cyan]Навчання:[/cyan]
  [yellow]Група:[/yellow] {student.group_name}
  [yellow]Курс:[/yellow] {student.course_number} ({student.course_name})
  [yellow]Спеціальність:[/yellow] {student.specialty_name} ({student.specialty_code})
  [yellow]Рік вступу:[/yellow] {student.admission_year}
"""

    console.print(Panel(info_text, title=f"Студент ID {student.id}", border_style="green"))


if __name__ == "__main__":
    app()
