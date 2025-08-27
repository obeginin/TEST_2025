from my_wallet_service.utils.config import settings
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import logging
# Configure logging

def setup_logging():
    # Путь к папке с логами
    BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта
    log_dir = BASE_DIR / settings.log_file
    log_dir.mkdir(parents=True, exist_ok=True)

    # Полный путь к файлу логов
    log_path = log_dir / "app.log"
    #print(f"Рабочая директория: {os.getcwd()}")

    # Формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Основной обработчик для ротации логов
    file_handler = TimedRotatingFileHandler(
        filename=str(log_path),
        when="midnight",  # ротация раз в сутки
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    # Настройка корневого логгера
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), "INFO"),
        handlers=[file_handler, console_handler]
    )

    logging.info(f"Логирование инициализировано. Лог: {log_path}")