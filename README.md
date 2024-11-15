# Nutrition Bot API

**Nutrition Bot API** — это асинхронный API для обработки и анализа сообщений о питании пользователя. С его помощью можно извлекать ключевые данные из текстовых сообщений, уточнять детали и сохранять информацию о пищевых привычках пользователя. API поддерживает интеграцию с ботом Telegram для взаимодействия с пользователем в режиме реального времени.

## Описание

Nutrition Bot API предназначен для получения сообщений от пользователей, их обработки и сохранения данных о питании. API анализирует текстовые сообщения, извлекая действия, объекты (еду), количество и другие параметры. При необходимости, если данные неполные, API автоматически уточняет детали у пользователя, используя асинхронные очереди и Redis для обработки очереди сообщений.

### Основные функции
- **Анализ текстов**: Извлечение из сообщения действий, объектов, количества и других параметров с помощью NLP.
- **Уточнение данных**: Уточнение данных у пользователя через бот, если не все обязательные поля заполнены.
- **Тематический анализ**: Определение темы сообщения и фильтрация неподдерживаемых тем.
- **Интеграция с Redis**: Поддержка асинхронных очередей сообщений для пользователей и накопление данных для последующей отправки.
- **Отправка уведомлений**: Автоматическая отправка сообщений пользователю по результатам обработки (например, для уточнений или уведомлений).

## Структура проекта

- **backend** - Основная директория API и сервисов.
  - `services` - Логика обработки сообщений, анализа текста, управления темами и отправки уведомлений.
  - `models` - SQLAlchemy-модели для работы с базой данных.
  - `repositories` - Реализация репозиториев для работы с сущностями базы данных.
  - `schemas` - Pydantic-схемы для валидации входящих данных.
  - `utils` - Утилиты для работы с Redis и вспомогательные функции.
- **alembic** - Каталог для управления миграциями базы данных.
- **bot** - Интеграция с Telegram Bot API, обработка и отправка сообщений пользователю.

## Установка и настройка

1. **Клонирование репозитория**:
   ```bash
   git clone <new-repo-url>
   cd Nutrition-Bot-API
   
2. **Установка зависимостей: Проект использует docker-compose для развёртывания**:
    ```bash
    docker-compose up --build

3. **Настройка переменных окружения**: В корневом каталоге создайте файл .env и добавьте необходимые переменные окружения (например, настройки базы данных, Redis, токен бота Telegram).

4. **Миграции базы данных**: Выполните миграции для создания необходимых таблиц в базе данных:
    ```bash
   docker-compose run --rm alembic upgrade head

## Поддержка и Контакты
Для получения дополнительной информации и поддержки обратитесь к разработчику или создайте issue в репозитории проекта.