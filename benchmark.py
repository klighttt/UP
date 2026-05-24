import time
import requests
from integration_service import IntegrationService

def benchmark():
    service = IntegrationService()
    start_total = time.perf_counter()

    # Шаг 1: получение активного теста
    start = time.perf_counter()
    test = service.get_active_test()
    t1 = time.perf_counter() - start
    print(f"Получение теста: {t1:.3f} сек")

    # Шаг 2: получение вопросов
    start = time.perf_counter()
    questions = service.get_questions(test["id"])
    t2 = time.perf_counter() - start
    print(f"Получение вопросов: {t2:.3f} сек")

    # Шаг 3: проверка ответов
    answers = [
        {"questionId": q["id"], "selectedOption": q["correctAnswer"]}
        for q in questions
    ]
    start = time.perf_counter()
    result = service.check_answers(test["id"], 1, answers)
    t3 = time.perf_counter() - start
    print(f"Проверка ответов: {t3:.3f} сек")

    # Шаг 4: сохранение результата
    start = time.perf_counter()
    saved = service.save_result({
        "testId": test["id"], "userId": 1, "score": result["score"],
        "maxScore": result["maxScore"], "percentage": result["percentage"],
        "passed": result["passed"], "completedAt": result["completedAt"],
        "details": result["details"]
    })
    t4 = time.perf_counter() - start
    print(f"Сохранение результата: {t4:.3f} сек")

    total = time.perf_counter() - start_total
    print(f"\nОбщее время выполнения сценария: {total:.3f} сек")
    return total

if __name__ == "__main__":
    benchmark()