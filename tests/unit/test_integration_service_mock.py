import pytest
from unittest.mock import patch, Mock
import requests
from integration_service import IntegrationService

@pytest.fixture
def service():
    return IntegrationService()

def test_get_active_test_success(service):
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": 1, "title": "Test"}
    with patch('requests.get', return_value=fake_response) as mock_get:
        result = service.get_active_test()
        assert result == {"id": 1, "title": "Test"}
        mock_get.assert_called_once_with("http://localhost:5001/tests/active", timeout=5)

def test_get_active_test_failure(service):
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(Exception):
            service.get_active_test()

def test_check_answers_success(service):
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"score": 100, "passed": True}
    with patch('requests.post', return_value=fake_response) as mock_post:
        result = service.check_answers(1, 1, [{"questionId": 1, "selectedOption": "print"}])
        assert result["score"] == 100
        mock_post.assert_called_once()