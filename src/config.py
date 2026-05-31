from pydantic_settings import BaseSettings
from pydantic import Field, computed_field


class Settings(BaseSettings):
    """Налаштування додатка."""

    db_host: str = Field(
        default="localhost",
        description="PostgreSQL host"
    )

    db_port: int = Field(
        default=5432,
        description="PostgreSQL port"
    )

    db_user: str = Field(
        default="student_user",
        description="PostgreSQL username"
    )

    db_password: str = Field(
        default="student_pass",
        description="PostgreSQL password"
    )

    db_name: str = Field(
        default="students_db",
        description="PostgreSQL database name"
    )

    database_schema: str = Field(
        default="s_university",
        description="Схема бази даних"
    )

    app_name: str = Field(
        default="Student Directory API",
        description="Назва додатка"
    )

    app_version: str = Field(
        default="1.0.0",
        description="Версія додатка"
    )

    debug: bool = Field(
        default=True,
        description="Режим налагодження"
    )

    api_prefix: str = Field(
        default="/api",
        description="Префікс для API endpoints"
    )

    api_host: str = Field(
        default="0.0.0.0",
        description="Host для API сервера"
    )

    api_port: int = Field(
        default=8000,
        description="Port для API сервера"
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:8000"],
        description="Дозволені CORS origins"
    )

    @computed_field
    @property
    def database_url(self) -> str:
        """
        Побудувати database URL з компонентів.

        Returns:
            str: PostgreSQL connection URL
        """
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore" 
    }


settings = Settings()


def get_database_url() -> str:
    """
    Отримати URL підключення до бази даних.

    Returns:
        str: Database URL
    """
    return settings.database_url


def get_database_schema() -> str:
    """
    Отримати назву схеми бази даних.

    Returns:
        str: Назва схеми (s_university)
    """
    return settings.database_schema


def get_settings() -> Settings:
    """
    Отримати налаштування додатка.

    Returns:
        Settings: Об'єкт налаштувань
    """
    return settings
