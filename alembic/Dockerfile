# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements для установки зависимостей
COPY alembic/requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Устанавливаем переменную PYTHONPATH
ENV PYTHONPATH="/app/backend"

# Копируем всю папку alembic (включая alembic.ini и папку versions)
COPY alembic /app/alembic

# Копируем папку backend, чтобы Alembic мог найти необходимые модели и модули
COPY backend /app/backend

# Указываем рабочую директорию для Alembic
WORKDIR /app/alembic

# Запуск Alembic для применения миграций
CMD ["alembic", "upgrade", "head"]
