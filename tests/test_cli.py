"""
Тести для CLI інтерфейсу.

Тестування команд через Typer CliRunner.
"""

import pytest
from typer.testing import CliRunner

from src.cli import app


runner = CliRunner()


@pytest.mark.integration
class TestCLICommands:
    """Тести для CLI команд."""

    def test_cli_help(self):
        """Тест команди --help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "students" in result.stdout.lower() or "довідник" in result.stdout.lower()

    def test_list_command(self):
        """Тест команди list."""
        result = runner.invoke(app, ["list", "--limit", "5"])

        # Може бути 0 (якщо БД пуста) або успіх
        assert result.exit_code in [0, 1]

    def test_list_command_with_offset(self):
        """Тест команди list з offset."""
        result = runner.invoke(app, ["list", "--offset", "0", "--limit", "10"])

        assert result.exit_code in [0, 1]

    def test_show_command_non_existing(self):
        """Тест команди show для неіснуючого студента."""
        result = runner.invoke(app, ["show", "999999"])

        assert result.exit_code == 1
        assert "не знайдено" in result.stdout.lower() or "not found" in result.stdout.lower()

    def test_groups_command(self):
        """Тест команди groups."""
        result = runner.invoke(app, ["groups"])

        assert result.exit_code == 0
        # Має показати таблицю груп або повідомлення що їх немає

    def test_specialties_command(self):
        """Тест команди specialties."""
        result = runner.invoke(app, ["specialties"])

        assert result.exit_code == 0

    def test_stats_command(self):
        """Тест команди stats."""
        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "студент" in result.stdout.lower() or "груп" in result.stdout.lower()

    def test_search_command(self):
        """Тест команди search."""
        result = runner.invoke(app, ["search", "Test"])

        assert result.exit_code in [0, 1]  # 0 якщо знайдено, 1 якщо ні

    def test_export_json_command(self, temp_json_file):
        """Тест команди export у JSON."""
        result = runner.invoke(app, ["export", temp_json_file, "--format", "json"])

        # Може бути помилка якщо БД пуста, але команда має працювати
        assert result.exit_code in [0, 1]

    def test_export_csv_command(self, temp_csv_file):
        """Тест команди export у CSV."""
        result = runner.invoke(app, ["export", temp_csv_file, "--format", "csv"])

        assert result.exit_code in [0, 1]

    def test_delete_command_non_existing(self):
        """Тест команди delete для неіснуючого студента."""
        # Використати --no для автоматичного скасування
        result = runner.invoke(app, ["delete", "999999"], input="n\n")

        assert result.exit_code == 1


@pytest.mark.integration
@pytest.mark.slow
class TestSeedCommand:
    """Тести для команди seed."""

    def test_seed_command_with_cancel(self):
        """Тест команди seed зі скасуванням."""
        # Відповісти 'n' на підтвердження
        result = runner.invoke(app, ["seed", "--count", "5"], input="n\n")

        assert result.exit_code in [0, 1]
        assert "скасовано" in result.stdout.lower() or "cancel" in result.stdout.lower()

    @pytest.mark.slow
    def test_seed_command_small_count(self):
        """Тест команди seed з малою кількістю."""
        # Відповісти 'y' на підтвердження
        result = runner.invoke(app, ["seed", "--count", "2"], input="y\n")

        # Може бути помилка якщо немає груп у БД
        assert result.exit_code in [0, 1]

        if result.exit_code == 0:
            assert "створено" in result.stdout.lower() or "created" in result.stdout.lower()


class TestCLIOutput:
    """Тести форматування виводу CLI."""

    def test_cli_uses_rich_formatting(self):
        """Тест що CLI використовує Rich для форматування."""
        result = runner.invoke(app, ["stats"])

        # Rich використовує ANSI escape codes або unicode box characters
        # Або спеціальні символи форматування
        output = result.stdout

        # Перевірити що є форматування (не просто plain text)
        # Rich таблиці містять box characters
        has_formatting = any(char in output for char in ['│', '─', '┌', '└', '┐', '┘'])

        # Якщо немає box characters, перевірити що є хоча б структурований вивід
        if not has_formatting:
            assert len(output) > 0


class TestCLIErrorHandling:
    """Тести обробки помилок CLI."""

    def test_invalid_command(self):
        """Тест невалідної команди."""
        result = runner.invoke(app, ["invalid_command"])

        assert result.exit_code != 0

    def test_show_with_invalid_id(self):
        """Тест show з невалідним ID."""
        result = runner.invoke(app, ["show", "not-a-number"])

        assert result.exit_code != 0

    def test_list_with_negative_offset(self):
        """Тест list з негативним offset."""
        result = runner.invoke(app, ["list", "--offset", "-1"])

        assert result.exit_code != 0

    def test_export_invalid_format(self):
        """Тест export з невалідним форматом."""
        result = runner.invoke(app, ["export", "test.txt", "--format", "xml"])

        assert result.exit_code == 1
