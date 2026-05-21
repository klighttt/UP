"""
Интеграционный сервис (оркестратор) с логированием, Retry и Circuit Breaker.
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from logger_config import setup_logging
from resilience import resilient_call

# Инициализация логирования (JSON + консоль)
logger = setup_logging()


class IntegrationService:
    """Интеграционный сервис для оркестрации модулей тестирования"""

    def __init__(self):
        self.module_a_url = "http://localhost:5001"
        self.module_b_url = "http://localhost:5002"
        self.module_c_url = "http://localhost:3000"
        logger.info("IntegrationService инициализирован")

    @resilient_call
    def get_active_test(self) -> Optional[Dict[str, Any]]:
        """Вызов модуля А: получение активного теста"""
        logger.info("Вызов модуля А: GET /tests/active")
        try:
            response = requests.get(f"{self.module_a_url}/tests/active", timeout=5)
            response.raise_for_status()
            test_data = response.json()
            logger.info(f"Модуль А ответил: тест ID={test_data.get('id')}")
            return test_data
        except Exception as e:
            logger.error(f"Ошибка вызова модуля А: {e}")
            raise

    @resilient_call
    def get_questions(self, test_id: int) -> Optional[List[Dict[str, Any]]]:
        """Вызов модуля А: получение вопросов теста"""
        logger.info(f"Вызов модуля А: GET /tests/{test_id}/questions")
        try:
            response = requests.get(
                f"{self.module_a_url}/tests/{test_id}/questions",
                timeout=5
            )
            response.raise_for_status()
            questions = response.json()
            logger.info(f"Модуль А вернул {len(questions)} вопросов")
            return questions
        except Exception as e:
            logger.error(f"Ошибка вызова модуля А (вопросы): {e}")
            raise

    @resilient_call
    def check_answers(self, test_id: int, user_id: int, answers: List[Dict]) -> Optional[Dict[str, Any]]:
        """Вызов модуля Б: проверка ответов"""
        payload = {
            "userId": user_id,
            "answers": answers
        }
        logger.info(f"Вызов модуля Б: POST /tests/{test_id}/submit")
        logger.info(f"Проверка ответов для пользователя {user_id}")
        try:
            response = requests.post(
                f"{self.module_b_url}/tests/{test_id}/submit",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Модуль Б ответил: баллы={result.get('score')}, пройден={result.get('passed')}")
            return result
        except Exception as e:
            logger.error(f"Ошибка вызова модуля Б: {e}")
            raise

    @resilient_call
    def save_result(self, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Вызов модуля В: сохранение результата"""
        logger.info("Вызов модуля В: POST /results/save")
        try:
            response = requests.post(
                f"{self.module_c_url}/results/save",
                json=result_data,
                timeout=5
            )
            response.raise_for_status()
            saved = response.json()
            logger.info(f"Модуль В сохранил результат: {saved.get('resultId')}")
            return saved
        except Exception as e:
            logger.error(f"Ошибка вызова модуля В: {e}")
            raise

    @resilient_call
    def get_user_results(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Вызов модуля В: получение истории результатов"""
        logger.info(f"Вызов модуля В: GET /results/{user_id}")
        try:
            response = requests.get(
                f"{self.module_c_url}/results/{user_id}",
                timeout=5
            )
            response.raise_for_status()
            results = response.json()
            logger.info(f"Модуль В вернул {results.get('totalAttempts')} попыток")
            return results
        except Exception as e:
            logger.error(f"Ошибка вызова модуля В (история): {e}")
            raise

    def complete_test_flow(self, user_id: int, answers: List[Dict]) -> Dict[str, Any]:
        """
        Полный сценарий тестирования (оркестрация):
        1. Получить активный тест (модуль А)
        2. Проверить ответы (модуль Б)
        3. Сохранить результат (модуль В)
        """
        logger.info(f"=== НАЧАЛО ПОЛНОГО СЦЕНАРИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ {user_id} ===")

        # Шаг 1: получить тест
        test = self.get_active_test()
        if not test:
            logger.error("Не удалось получить тест")
            return {"error": "Не удалось получить тест", "status": "failed"}

        test_id = test.get("id")

        # Шаг 2: проверить ответы
        check_result = self.check_answers(test_id, user_id, answers)
        if not check_result:
            logger.error("Не удалось проверить ответы")
            return {"error": "Не удалось проверить ответы", "status": "failed"}

        # Шаг 3: сохранить результат
        save_payload = {
            "testId": test_id,
            "userId": user_id,
            "score": check_result.get("score"),
            "maxScore": check_result.get("maxScore"),
            "percentage": check_result.get("percentage"),
            "passed": check_result.get("passed"),
            "completedAt": check_result.get("completedAt"),
            "details": check_result.get("details")
        }
        saved = self.save_result(save_payload)

        logger.info(f"=== СЦЕНАРИЙ ЗАВЕРШЁН: баллы={check_result.get('score')} ===")

        return {
            "status": "success",
            "test": test,
            "result": check_result,
            "saved": saved
        }


# Маппер данных (аналог AutoMapper)
class AnswerMapper:
    """Преобразование данных между форматами разных модулей"""

    @staticmethod
    def map_user_answers(answers_dict: Dict[int, str]) -> List[Dict]:
        """Преобразование словаря ответов в формат для модуля Б"""
        result = []
        for q_id, answer in answers_dict.items():
            result.append({
                "questionId": q_id,
                "selectedOption": answer
            })
        return result

    @staticmethod
    def map_to_save_format(result_data: Dict) -> Dict:
        """Преобразование результата от модуля Б в формат для модуля В"""
        return {
            "testId": result_data.get("testId"),
            "userId": result_data.get("userId"),
            "score": result_data.get("score"),
            "maxScore": result_data.get("maxScore"),
            "percentage": result_data.get("percentage"),
            "passed": result_data.get("passed"),
            "completedAt": result_data.get("completedAt"),
            "details": result_data.get("details")
        }


# Пример использования
if __name__ == "__main__":
    orchestrator = IntegrationService()

    # Пример правильных ответов
    sample_answers = [
        {"questionId": 1, "selectedOption": "Объектно-ориентированное программирование"},
        {"questionId": 2, "selectedOption": "#"},
        {"questionId": 3, "selectedOption": "tuple"},
        {"questionId": 4, "selectedOption": "print()"},
        {"questionId": 5, "selectedOption": "80"}
    ]

    result = orchestrator.complete_test_flow(user_id=1, answers=sample_answers)
    print("\n" + "="*50)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ ОРКЕСТРАЦИИ:")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))