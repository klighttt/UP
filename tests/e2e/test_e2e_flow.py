import pytest
from playwright.sync_api import sync_playwright
import requests
import time

@pytest.fixture(scope="module")
def base_url():
    return "http://localhost:5001"  # фронтенд index.html открыт локально

def test_full_test_flow():
    # Предварительно убеждаемся, что модули работают
    try:
        requests.get("http://localhost:5001/tests/active", timeout=2)
        requests.get("http://localhost:5002/docs", timeout=2)
        requests.get("http://localhost:3000/results/1", timeout=2)
    except Exception:
        pytest.skip("Модули не запущены, пропускаем E2E тест")

    with sync_playwright() as p:
        # Открываем HTML файл напрямую (можно через file://)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # index.html должен быть доступен. Можно запустить простой HTTP сервер или открыть файл
        page.goto("file:///C:/Users/tw1nk/Desktop/testing-system/index.html")
        # Ждём загрузки теста
        page.wait_for_selector(".card-header:has-text('Вопросы теста')", timeout=10000)

        # Находим все вопросы (допустим 5 вопросов)
        questions = page.query_selector_all(".card-header.bg-white.fw-bold")
        assert len(questions) == 5

        # Выбираем первый вариант в каждом вопросе (имитация выбора)
        for i in range(1, 6):
            options = page.query_selector_all(f"#q-{i} .option-item")
            if options:
                options[0].click()
                time.sleep(0.2)

        # Нажимаем отправить
        page.click("#submitBtn")
        # Ждём появления результата
        page.wait_for_selector("#resultCard .alert", timeout=10000)

        # Проверяем, что результат отображает баллы
        result_text = page.inner_text("#resultCard")
        assert "Баллы:" in result_text

        # Также проверим через API модуля В, что результат сохранён для user_id=1
        resp = requests.get("http://localhost:3000/results/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalAttempts"] >= 1

        browser.close()