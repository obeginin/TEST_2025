# Используем официальный Python образ
FROM python:3.12-slim

# Указываем переменные окружения (опционально)
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка зависимостей системы (gcc нужен для некоторых Python-пакетов)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем весь проект в контейнер
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888", "--reload"]