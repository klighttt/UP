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

logger = setup_logging()


class IntegrationService:
    def __init__(self):
        self.module_a_url = "http://localhost:5001"
        self.module_b_url = "http://localhost:5002"
        self.module_c_url = "http://localhost:3000"
        logger.info("IntegrationService инициализирован")

    @resilient_call
    def get_active_test(self) -> Optional[Dict[str, Any]]:
        logger.info("Вызов модуля А: GET /tests/active")
        response = requests.get(f"{self.module_a_url}/tests/active", timeout=5)
        response.raise_for_status()
        test_data = response.json()
        logger.info(f"Модуль А ответил: тест ID={test_data.get('id')}")
        return test_data

    @resilient_call
    def get_questions(self, test_id: int) -> Optional[List[Dict[str, Any]]]:
        logger.info(f"Вызов модуля А: GET /tests/{test_id}/questions")
        response = requests.get(f"{self.module_a_url}/tests/{test_id}/questions", timeout=5)
        response.raise_for_status()
        questions = response.json()
        logger.info(f"Модуль А вернул {len(questions)} вопросов")
        return questions

    @resilient_call
    def check_answers(self, test_id: int, user_id: int, answers: List[Dict]) -> Optional[Dict[str, Any]]:
        payload = {"userId": user_id, "answers": answers}
        logger.info(f"Вызов модуля Б: POST /tests/{test_id}/submit")
        response = requests.post(f"{self.module_b_url}/tests/{test_id}/submit", json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Модуль Б ответил: баллы={result.get('score')}, пройден={result.get('passed')}")
        return result

    @resilient_call
    def save_result(self, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info("Вызов модуля В: POST /results/save")
        response = requests.post(f"{self.module_c_url}/results/save", json=result_data, timeout=5)
        response.raise_for_status()
        saved = response.json()
        logger.info(f"Модуль В сохранил результат: {saved.get('resultId')}")
        return saved

    @resilient_call
    def get_user_results(self, user_id: int) -> Optional[Dict[str, Any]]:
        logger.info(f"Вызов модуля В: GET /results/{user_id}")
        response = requests.get(f"{self.module_c_url}/results/{user_id}", timeout=5)
        response.raise_for_status()
        results = response.json()
        logger.info(f"Модуль В вернул {results.get('totalAttempts')} попыток")
        return results

    def complete_test_flow(self, user_id: int, answers: List[Dict]) -> Dict[str, Any]:
        logger.info(f"=== НАЧАЛО ПОЛНОГО СЦЕНАРИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ {user_id} ===")
        test = self.get_active_test()
        if not test:
            return {"error": "Не удалось получить тест", "status": "failed"}
        test_id = test.get("id")
        check_result = self.check_answers(test_id, user_id, answers)
        if not check_result:
            return {"error": "Не удалось проверить ответы", "status": "failed"}
        save_payload = {
            "testId": test_id, "userId": user_id,
            "score": check_result.get("score"), "maxScore": check_result.get("maxScore"),
            "percentage": check_result.get("percentage"), "passed": check_result.get("passed"),
            "completedAt": check_result.get("completedAt"), "details": check_result.get("details")
        }
        saved = self.save_result(save_payload)
        logger.info(f"=== СЦЕНАРИЙ ЗАВЕРШЁН: баллы={check_result.get('score')} ===")
        return {"status": "success", "test": test, "result": check_result, "saved": saved}


class AnswerMapper:
    @staticmethod
    def map_user_answers(answers_dict: Dict[int, str]) -> List[Dict]:
        return [{"questionId": q_id, "selectedOption": answer} for q_id, answer in answers_dict.items()]

    @staticmethod
    def map_to_save_format(result_data: Dict) -> Dict:
        return {
            "testId": result_data.get("testId"), "userId": result_data.get("userId"),
            "score": result_data.get("score"), "maxScore": result_data.get("maxScore"),
            "percentage": result_data.get("percentage"), "passed": result_data.get("passed"),
            "completedAt": result_data.get("completedAt"), "details": result_data.get("details")
        }


if __name__ == "__main__":
    orchestrator = IntegrationService()
    sample_answers = [
        {"questionId": 1, "selectedOption": "Объектно-ориентированное программирование"},
        {"questionId": 2, "selectedOption": "#"}, {"questionId": 3, "selectedOption": "tuple"},
        {"questionId": 4, "selectedOption": "print()"}, {"questionId": 5, "selectedOption": "80"}
    ]
    result = orchestrator.complete_test_flow(user_id=1, answers=sample_answers)
    print(json.dumps(result, indent=2, ensure_ascii=False))