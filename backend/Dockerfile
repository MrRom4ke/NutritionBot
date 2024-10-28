# Базовый образ Python
FROM python:3.12-slim

# Рабочая директория
WORKDIR /backend

# Копия файла зависимостей
COPY requirements.txt ./

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов в рабочую директорию
COPY . .

# Установите PYTHONPATH
ENV PYTHONPATH=/backend

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
