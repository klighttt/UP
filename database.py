import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional

DATABASE_PATH = "testing_system.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                time_limit_minutes INTEGER DEFAULT 30,
                max_score INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                type TEXT DEFAULT 'single',
                correct_answer TEXT NOT NULL,
                FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                score INTEGER,
                max_score INTEGER,
                percentage REAL,
                passed BOOLEAN,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                payload TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        ''')

        cursor.execute("SELECT COUNT(*) FROM tests")
        if cursor.fetchone()[0] == 0:
            _insert_sample_data(cursor)

        print("База данных инициализирована")


def _insert_sample_data(cursor):
    cursor.execute('''
        INSERT INTO tests (title, description, time_limit_minutes, max_score)
        VALUES (?, ?, ?, ?)
    ''', ("Основы программирования", "Тест проверяет базовые знания", 30, 100))
    test_id = cursor.lastrowid

    questions_data = [
        ("Что означает аббревиатура ООП?", "Объектно-ориентированное программирование"),
        ("Какой символ используется для комментария в Python?", "#"),
        ("Какой тип данных в Python является неизменяемым?", "tuple"),
        ("Какая функция выводит информацию в Python?", "print()"),
        ("Какой порт используется для HTTP по умолчанию?", "80"),
    ]

    for q_text, correct in questions_data:
        cursor.execute('''
            INSERT INTO questions (test_id, text, correct_answer)
            VALUES (?, ?, ?)
        ''', (test_id, q_text, correct))


class TestRepository:
    @staticmethod
    def get_all_tests() -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tests")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_test_by_id(test_id: int) -> Optional[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tests WHERE id = ?", (test_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_questions_with_options(test_id: int) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE test_id = ?", (test_id,))
            questions = [dict(row) for row in cursor.fetchall()]

            for q in questions:
                cursor.execute(
                    "SELECT option_text FROM question_options WHERE question_id = ?",
                    (q["id"],)
                )
                q["options"] = [row["option_text"] for row in cursor.fetchall()]

            return questions


class ResultRepository:
    @staticmethod
    def save_result(test_id: int, user_id: int, score: int, max_score: int,
                    percentage: float, passed: bool, details: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_results (test_id, user_id, score, max_score, percentage, passed, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (test_id, user_id, score, max_score, percentage, passed, details))
            return cursor.lastrowid

    @staticmethod
    def get_user_results(user_id: int) -> List[Dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM test_results WHERE user_id = ? ORDER BY completed_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_analytics(test_id: int) -> Dict:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT AVG(percentage) as avg_percentage,
                       COUNT(*) as attempts_count,
                       SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count
                FROM test_results
                WHERE test_id = ?
            ''', (test_id,))
            row = cursor.fetchone()
            return dict(row) if row else {"avg_percentage": 0, "attempts_count": 0, "passed_count": 0}


if __name__ == "__main__":
    init_database()