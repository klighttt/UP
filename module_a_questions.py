from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# База данных тестов
tests = {
    1: {
        "id": 1,
        "title": "Основы программирования",
        "description": "Тест проверяет базовые знания программирования",
        "timeLimitMinutes": 30,
        "maxScore": 100
    }
}

# База данных вопросов (10 вопросов)
questions = {
    1: [
        {
            "id": 1,
            "text": "Что означает аббревиатура ООП?",
            "options": ["Объектно-ориентированное программирование", "Оперативное объединение программ", "Основные основы программирования", "Общее описание процессов"],
            "type": "single",
            "correctAnswer": "Объектно-ориентированное программирование"
        },
        {
            "id": 2,
            "text": "Какой символ используется для однострочного комментария в Python?",
            "options": ["//", "<!-- -->", "#", "/* */"],
            "type": "single",
            "correctAnswer": "#"
        },
        {
            "id": 3,
            "text": "Какой тип данных в Python является неизменяемым?",
            "options": ["list", "dict", "tuple", "set"],
            "type": "single",
            "correctAnswer": "tuple"
        },
        {
            "id": 4,
            "text": "Какая функция используется для вывода информации в Python?",
            "options": ["input()", "print()", "output()", "display()"],
            "type": "single",
            "correctAnswer": "print()"
        },
        {
            "id": 5,
            "text": "Что делает оператор '==' в Python?",
            "options": ["Присваивание", "Сравнение на равенство", "Сравнение на неравенство", "Сложение"],
            "type": "single",
            "correctAnswer": "Сравнение на равенство"
        },
        {
            "id": 6,
            "text": "Какой цикл выполняется пока условие истинно?",
            "options": ["for", "while", "do-while", "foreach"],
            "type": "single",
            "correctAnswer": "while"
        },
        {
            "id": 7,
            "text": "Что такое API?",
            "options": [
                "Интерфейс программирования приложений",
                "Язык программирования",
                "База данных",
                "Операционная система"
            ],
            "type": "single",
            "correctAnswer": "Интерфейс программирования приложений"
        },
        {
            "id": 8,
            "text": "Какой метод HTTP используется для получения данных?",
            "options": ["POST", "PUT", "GET", "DELETE"],
            "type": "single",
            "correctAnswer": "GET"
        },
        {
            "id": 9,
            "text": "Что означает SQL?",
            "options": [
                "Structured Query Language",
                "Simple Query Language",
                "Standard Question Language",
                "System Query Logic"
            ],
            "type": "single",
            "correctAnswer": "Structured Query Language"
        },
        {
            "id": 10,
            "text": "Какой порт используется для HTTP по умолчанию?",
            "options": ["21", "22", "80", "443"],
            "type": "single",
            "correctAnswer": "80"
        }
    ]
}

@app.route('/tests/active', methods=['GET'])
def get_active_test():
    first_test = list(tests.values())[0]
    return jsonify(first_test)

@app.route('/tests/<int:test_id>/questions', methods=['GET'])
def get_questions(test_id):
    if test_id not in questions:
        return jsonify({"error": "Тест не найден"}), 404
    
    safe_questions = []
    for q in questions[test_id]:
        safe_questions.append({
            "id": q["id"],
            "text": q["text"],
            "options": q["options"],
            "type": q["type"]
        })
    return jsonify(safe_questions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)