"""
Точка входу для запуску API сервера.

Запуск: python -m src.main
"""

import uvicorn
from src.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
