# Используем официальный образ Python
FROM python:3.12-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /bot

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Команда для запуска бота
CMD ["python", "main.py"]