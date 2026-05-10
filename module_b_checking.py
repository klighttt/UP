from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Сервис проверки ответов")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Правильные ответы для 10 вопросов (id -> правильный ответ)
correct_answers_db = {
    1: "Объектно-ориентированное программирование",
    2: "#",
    3: "tuple",
    4: "print()",
    5: "Сравнение на равенство",
    6: "while",
    7: "Интерфейс программирования приложений",
    8: "GET",
    9: "Structured Query Language",
    10: "80"
}

class AnswerItem(BaseModel):
    questionId: int
    selectedOption: str

class SubmitRequest(BaseModel):
    userId: int
    answers: List[AnswerItem]

class SubmitResponse(BaseModel):
    testId: int
    userId: int
    score: int
    maxScore: int
    percentage: float
    passed: bool
    completedAt: str
    details: Dict[int, bool]
    incorrectAnswers: Dict[int, Dict[str, str]]

@app.post("/tests/{test_id}/submit")
async def submit_answers(test_id: int, request: SubmitRequest):
    total_questions = len(request.answers)
    correct_count = 0
    details = {}
    incorrect_answers = {}
    
    for answer in request.answers:
        question_id = answer.questionId
        user_answer = answer.selectedOption
        correct_answer = correct_answers_db.get(question_id)
        
        is_correct = (user_answer == correct_answer)
        if is_correct:
            correct_count += 1
        else:
            incorrect_answers[question_id] = {
                "user_answer": user_answer,
                "correct_answer": correct_answer
            }
        details[question_id] = is_correct
    
    from datetime import datetime
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    return {
        "testId": test_id,
        "userId": request.userId,
        "score": score,
        "maxScore": 100,
        "percentage": float(score),
        "passed": score >= 60,
        "completedAt": datetime.now().isoformat(),
        "details": details,
        "incorrectAnswers": incorrect_answers
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)