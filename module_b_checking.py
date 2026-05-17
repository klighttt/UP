from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

correct_answers_db = {
    1: "Объектно-ориентированное программирование",
    2: "#",
    3: "tuple",
    4: "print()",
    5: "80"
}

class AnswerItem(BaseModel):
    questionId: int
    selectedOption: str


class SubmitRequest(BaseModel):
    userId: int
    answers: List[AnswerItem]


@app.post("/tests/{test_id}/submit")
async def submit_answers(test_id: int, request: SubmitRequest):
    # ... код ...


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)