from database import init_database, webhook_manager, WebhookEvent
import requests
import time

# Инициализация БД
init_database()

# Эмуляция модуля В (результаты) — подписчик на вебхуки
print("Эмуляция работы вебхуков...")
print("1. Модуль А создаёт новый тест")
print("2. Отправляется вебхук в модуль Б и модуль В")
print("3. Модуль В сохраняет уведомление в своей БД")

# Создаём событие о завершении теста
event = WebhookEvent(
    event_type="test.completed",
    entity_type="result",
    entity_id=123,
    payload={
        "user_id": 1,
        "score": 85,
        "percentage": 85.0,
        "test_title": "Основы программирования"
    }
)

# Отправляем вебхук
print("\nОтправка вебхука...")
webhook_manager.send_event(event)

print("\nДемонстрация завершена.")