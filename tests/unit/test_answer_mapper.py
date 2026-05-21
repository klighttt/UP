import pytest
from integration_service import AnswerMapper

def test_map_user_answers():
    input_dict = {1: "print()", 2: "tuple", 3: "#"}
    expected = [
        {"questionId": 1, "selectedOption": "print()"},
        {"questionId": 2, "selectedOption": "tuple"},
        {"questionId": 3, "selectedOption": "#"}
    ]
    result = AnswerMapper.map_user_answers(input_dict)
    assert result == expected

def test_map_to_save_format():
    input_result = {
        "testId": 1,
        "userId": 101,
        "score": 80,
        "maxScore": 100,
        "percentage": 80.0,
        "passed": True,
        "completedAt": "2025-01-01T12:00:00",
        "details": {1: True, 2: False}
    }
    expected = {
        "testId": 1,
        "userId": 101,
        "score": 80,
        "maxScore": 100,
        "percentage": 80.0,
        "passed": True,
        "completedAt": "2025-01-01T12:00:00",
        "details": {1: True, 2: False}
    }
    result = AnswerMapper.map_to_save_format(input_result)
    assert result == expected