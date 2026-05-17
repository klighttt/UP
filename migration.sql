-- ============================================
-- МИГРАЦИЯ БАЗЫ ДАННЫХ
-- Система тестирования знаний
-- ============================================

-- Таблица: тесты
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    time_limit_minutes INTEGER DEFAULT 30,
    max_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица: вопросы
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    type TEXT DEFAULT 'single',
    correct_answer TEXT NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Таблица: варианты ответов
CREATE TABLE IF NOT EXISTS question_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Таблица: результаты тестирования
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
);

-- Таблица: события синхронизации (вебхуки)
CREATE TABLE IF NOT EXISTS sync_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    payload TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_questions_test_id ON questions(test_id);
CREATE INDEX IF NOT EXISTS idx_results_user_id ON test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_test_id ON test_results(test_id);
CREATE INDEX IF NOT EXISTS idx_events_status ON sync_events(status);

-- ============================================
-- ТЕСТОВЫЕ ДАННЫЕ
-- ============================================

INSERT OR IGNORE INTO tests (id, title, description, time_limit_minutes, max_score)
VALUES (1, 'Основы программирования', 'Тест проверяет базовые знания программирования', 30, 100);

INSERT OR IGNORE INTO questions (id, test_id, text, correct_answer)
VALUES 
    (1, 1, 'Что означает аббревиатура ООП?', 'Объектно-ориентированное программирование'),
    (2, 1, 'Какой символ используется для комментария в Python?', '#'),
    (3, 1, 'Какой тип данных в Python является неизменяемым?', 'tuple'),
    (4, 1, 'Какая функция выводит информацию в Python?', 'print()'),
    (5, 1, 'Какой порт используется для HTTP по умолчанию?', '80');