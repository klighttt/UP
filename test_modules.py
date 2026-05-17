import unittest
import sys
import os

# Добавляем пути к модулям, чтобы их импортировать
sys.path.append(os.path.dirname(__file__))

class TestModuleA(unittest.TestCase):
    def test_flask_app_exists(self):
        from module_a_questions import app
        self.assertIsNotNone(app)
        
    def test_test_data(self):
        from module_a_questions import tests, questions
        self.assertIn(1, tests)
        self.assertEqual(len(questions[1]), 10)

class TestModuleB(unittest.TestCase):
    def test_fastapi_app_exists(self):
        from module_b_checking import app
        self.assertIsNotNone(app)
        
    def test_correct_answers(self):
        from module_b_checking import correct_answers_db
        self.assertEqual(len(correct_answers_db), 10)
        self.assertEqual(correct_answers_db[10], "80")

if __name__ == '__main__':
    unittest.main()