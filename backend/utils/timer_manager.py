import asyncio
from datetime import datetime, timedelta


class TimerManager:
    def __init__(self):
        self.last_message_time = {}  # Время последнего сообщения для каждого пользователя
        self.timer_running = {}  # Флаг, указывающий, запущен ли таймер для пользователя

    async def start_timer(self, user_id: int, queue_manager):
        """Обновляет время последнего сообщения и запускает таймер, если он еще не запущен."""

        # Обновляем время последнего сообщения
        self.last_message_time[user_id] = datetime.now()

        # Если таймер не запущен, запускаем его
        if not self.timer_running.get(user_id):
            self.timer_running[user_id] = True
            asyncio.create_task(self.timer_task(user_id, queue_manager))

    async def timer_task(self, user_id: int, queue_manager):
        """Единый таймер, который ждёт 5 секунд тишины после последнего сообщения перед обработкой очереди."""
        while True:
            await asyncio.sleep(1)  # Проверка состояния каждые 1 секунду

            # Проверяем, прошло ли более 5 секунд с последнего сообщения
            time_since_last_message = datetime.now() - self.last_message_time[user_id]
            if time_since_last_message > timedelta(seconds=18):
                await queue_manager.process_queue()

                # Сбрасываем флаг таймера и завершаем задачу
                self.timer_running[user_id] = False
                break
            else:
                print(f"[{datetime.now()}] Таймер для пользователя {user_id} активен, ожидание тишины.")
