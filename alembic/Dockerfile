# Базовый образ Python
FROM python:3.12-slim

# Рабочая директория
WORKDIR /alembic

# Копия файла зависимостей
COPY requirements.txt ./

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов Alembic
COPY . .

# Установите PYTHONPATH
ENV PYTHONPATH=/backend

# Команда для выполнения миграции
CMD ["alembic", "upgrade", "head"]