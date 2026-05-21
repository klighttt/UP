import pytest
import requests
from integration_service import IntegrationService

@pytest.fixture(scope="module")
def service():
    return IntegrationService()

def test_get_active_test_real(service):
    result = service.get_active_test()
    assert result is not None
    assert "id" in result
    assert "title" in result

def test_get_questions_real(service):
    test = service.get_active_test()
    test_id = test["id"]
    questions = service.get_questions(test_id)
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert "text" in questions[0]

def test_check_answers_real(service):
    test = service.get_active_test()
    test_id = test["id"]
    answers = [{"questionId": 1, "selectedOption": "Объектно-ориентированное программирование"}]
    result = service.check_answers(test_id, 1, answers)
    assert result is not None
    assert "score" in result

def test_save_result_real(service):
    result_data = {
        "testId": 1,
        "userId": 99,
        "score": 100,
        "maxScore": 100,
        "percentage": 100.0,
        "passed": True,
        "completedAt": "2025-01-01T00:00:00",
        "details": "{}"
    }
    saved = service.save_result(result_data)
    assert saved is not None
    assert "resultId" in saved