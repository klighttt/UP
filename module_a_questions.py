from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tests = {
    1: {
        "id": 1,
        "title": "Основы программирования",
        "description": "Тест проверяет базовые знания",
        "timeLimitMinutes": 30,
        "maxScore": 100
    }
}

questions = {
    1: [
        {"id": 1, "text": "Что означает аббревиатура ООП?", "options": ["Объектно-ориентированное программирование", "Оперативное объединение программ", "Основные основы программирования", "Общее описание процессов"], "type": "single"},
        {"id": 2, "text": "Какой символ используется для комментария в Python?", "options": ["//", "<!-- -->", "#", "/* */"], "type": "single"},
        {"id": 3, "text": "Какой тип данных в Python является неизменяемым?", "options": ["list", "dict", "tuple", "set"], "type": "single"},
        {"id": 4, "text": "Какая функция выводит информацию в Python?", "options": ["input()", "print()", "output()", "display()"], "type": "single"},
        {"id": 5, "text": "Какой порт используется для HTTP по умолчанию?", "options": ["21", "22", "80", "443"], "type": "single"}
    ]
}

@app.route('/tests/active', methods=['GET'])
def get_active_test():
    return jsonify(tests[1])


@app.route('/tests/<int:test_id>/questions', methods=['GET'])
def get_questions(test_id):
    if test_id not in questions:
        return jsonify({"error": "Тест не найден"}), 404
    return jsonify(questions[test_id])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)