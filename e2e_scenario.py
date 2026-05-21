"""
Сквозной сценарий "Прохождение теста"
Реализация Saga pattern и state machine
"""

import time
import uuid
from enum import Enum
from typing import Dict, List, Optional
import requests

# ---------- State Machine ----------
class SessionState(Enum):
    NEW = "New"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class TestSession:
    """Конечный автомат сессии тестирования"""
    def __init__(self, session_id: str, test_id: int, user_id: int):
        self.session_id = session_id
        self.test_id = test_id
        self.user_id = user_id
        self.state = SessionState.NEW
        self.result = None

    def transition_to(self, new_state: SessionState):
        print(f"[State] Сессия {self.session_id}: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def start(self):
        if self.state == SessionState.NEW:
            self.transition_to(SessionState.IN_PROGRESS)
            return True
        return False

    def complete(self, result):
        if self.state == SessionState.IN_PROGRESS:
            self.result = result
            self.transition_to(SessionState.COMPLETED)
            return True
        return False

    def fail(self):
        if self.state == SessionState.IN_PROGRESS:
            self.transition_to(SessionState.FAILED)
            return True
        return False

# ---------- Saga Coordinator ----------
class SagaCoordinator:
    """Управляет транзакционностью шагов с компенсацией"""
    def __init__(self):
        self.steps = []
        self.compensations = []

    def add_step(self, name: str, action, compensation):
        self.steps.append((name, action, compensation))

    def execute(self):
        print("\n[Saga] Начало выполнения саги")
        for name, action, compensation in self.steps:
            try:
                print(f"[Saga] Выполнение шага: {name}")
                result = action()
                self.compensations.append((name, compensation))
                if result is False:
                    raise Exception(f"Шаг {name} вернул False")
            except Exception as e:
                print(f"[Saga] Ошибка на шаге {name}: {e}")
                self._compensate()
                return False
        print("[Saga] Сага выполнена успешно")
        return True

    def _compensate(self):
        print("[Saga] Запуск компенсации...")
        for name, compensation in reversed(self.compensations):
            try:
                print(f"[Saga] Компенсация шага: {name}")
                compensation()
            except Exception as e:
                print(f"[Saga] Ошибка при компенсации {name}: {e}")

# ---------- Бизнес-логика ----------
def check_test_availability(test_id: int) -> bool:
    """Проверка доступности теста (аналог stock check)"""
    print(f"[Check] Проверка теста {test_id} на доступность...")
    try:
        resp = requests.get(f"http://localhost:5001/tests/{test_id}/questions", timeout=3)
        if resp.status_code == 200:
            questions = resp.json()
            if len(questions) > 0:
                print("[Check] Тест доступен, вопросов: " + str(len(questions)))
                return True
        print("[Check] Тест не доступен (нет вопросов)")
        return False
    except Exception as e:
        print(f"[Check] Ошибка при проверке: {e}")
        return False

def submit_answers_and_save(test_id: int, user_id: int, answers: List[Dict]) -> Optional[Dict]:
    """Отправка ответов в модуль Б и сохранение результата в модуле В"""
    print("[Submit] Отправка ответов на проверку...")
    try:
        # Вызов модуля Б
        resp_b = requests.post(
            f"http://localhost:5002/tests/{test_id}/submit",
            json={"userId": user_id, "answers": answers},
            timeout=5
        )
        resp_b.raise_for_status()
        result_b = resp_b.json()
        print(f"[Submit] Результат проверки: баллы={result_b.get('score')}")

        # Сохранение в модуле В
        save_payload = {
            "testId": test_id,
            "userId": user_id,
            "score": result_b["score"],
            "maxScore": result_b["maxScore"],
            "percentage": result_b["percentage"],
            "passed": result_b["passed"],
            "completedAt": result_b["completedAt"],
            "details": result_b["details"]
        }
        resp_c = requests.post("http://localhost:3000/results/save", json=save_payload, timeout=5)
        resp_c.raise_for_status()
        print("[Submit] Результат сохранён")
        return result_b
    except Exception as e:
        print(f"[Submit] Ошибка: {e}")
        return None

def compensate_remove_session(session: TestSession):
    """Компенсация: удаление сессии"""
    print(f"[Compensation] Удаление сессии {session.session_id}")
    # Здесь можно удалить запись из БД, сейчас просто логируем

# ---------- Сквозной сценарий ----------
def run_end_to_end_scenario(user_id: int, test_id: int, answers: List[Dict]) -> bool:
    print("\n=== ЗАПУСК СКВОЗНОГО СЦЕНАРИЯ ===")
    session = TestSession(str(uuid.uuid4()), test_id, user_id)

    # Шаги саги
    saga = SagaCoordinator()

    # Шаг 1: проверка доступности теста
    def step1():
        return check_test_availability(test_id)

    def comp1():
        print("Компенсация: отмена выбора теста")

    # Шаг 2: старт сессии (переход в InProgress)
    def step2():
        return session.start()

    def comp2():
        compensate_remove_session(session)

    # Шаг 3: отправка ответов и сохранение
    def step3():
        result = submit_answers_and_save(test_id, user_id, answers)
        if result is None:
            return False
        session.complete(result)
        return True

    def comp3():
        print("Компенсация: удаление результата из БД")
        # Здесь запрос к модулю В на удаление, для простоты логируем

    saga.add_step("Проверка теста", step1, comp1)
    saga.add_step("Старт сессии", step2, comp2)
    saga.add_step("Проверка ответов и сохранение", step3, comp3)

    success = saga.execute()

    if success:
        print("\n=== СЦЕНАРИЙ УСПЕШНО ЗАВЕРШЁН ===")
        print(f"Статус сессии: {session.state.value}")
        if session.result:
            print(f"Баллы: {session.result['score']}")
    else:
        print("\n=== СЦЕНАРИЙ ПРОВАЛЕН (выполнена компенсация) ===")
        print(f"Статус сессии: {session.state.value}")

    return success

# ---------- Тестовый прогон ----------
if __name__ == "__main__":
    # Убедитесь, что модули А, Б, В запущены!
    # Пример правильных ответов
    sample_answers = [
        {"questionId": 1, "selectedOption": "Объектно-ориентированное программирование"},
        {"questionId": 2, "selectedOption": "#"},
        {"questionId": 3, "selectedOption": "tuple"},
        {"questionId": 4, "selectedOption": "print()"},
        {"questionId": 5, "selectedOption": "80"}
    ]
    success = run_end_to_end_scenario(user_id=1, test_id=1, answers=sample_answers)
    exit(0)