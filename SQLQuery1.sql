CREATE DATABASE TestingSystemDB;
GO

USE TestingSystemDB;
GO

-- Таблица: тесты
CREATE TABLE tests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    time_limit_minutes INT DEFAULT 30,
    max_score INT DEFAULT 100,
    created_at DATETIME DEFAULT GETDATE()
);

-- Таблица: вопросы
CREATE TABLE questions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_id INT NOT NULL,
    text NVARCHAR(MAX) NOT NULL,
    type NVARCHAR(20) DEFAULT 'single',
    correct_answer NVARCHAR(MAX) NOT NULL,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

-- Таблица: варианты ответов
CREATE TABLE question_options (
    id INT IDENTITY(1,1) PRIMARY KEY,
    question_id INT NOT NULL,
    option_text NVARCHAR(MAX) NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Таблица: результаты
CREATE TABLE test_results (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_id INT NOT NULL,
    user_id INT NOT NULL,
    score INT,
    max_score INT,
    percentage FLOAT,
    passed BIT,
    completed_at DATETIME DEFAULT GETDATE(),
    details NVARCHAR(MAX),
    FOREIGN KEY (test_id) REFERENCES tests(id)
);

-- Таблица: события вебхуков
CREATE TABLE sync_events (
    id INT IDENTITY(1,1) PRIMARY KEY,
    event_type NVARCHAR(100) NOT NULL,
    entity_type NVARCHAR(100) NOT NULL,
    entity_id INT NOT NULL,
    payload NVARCHAR(MAX),
    status NVARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT GETDATE(),
    processed_at DATETIME
);

-- Индексы
CREATE INDEX idx_questions_test_id ON questions(test_id);
CREATE INDEX idx_results_user_id ON test_results(user_id);
CREATE INDEX idx_results_test_id ON test_results(test_id);

-- Тестовые данные
INSERT INTO tests (title, description, time_limit_minutes, max_score)
VALUES ('Основы программирования', 'Тест проверяет базовые знания', 30, 100);

INSERT INTO questions (test_id, text, correct_answer)
VALUES 
    (1, 'Что означает аббревиатура ООП?', 'Объектно-ориентированное программирование'),
    (1, 'Какой символ используется для комментария в Python?', '#'),
    (1, 'Какой тип данных в Python является неизменяемым?', 'tuple'),
    (1, 'Какая функция выводит информацию в Python?', 'print()'),
    (1, 'Какой порт используется для HTTP по умолчанию?', '80');

-- Варианты ответов
INSERT INTO question_options (question_id, option_text) VALUES
(1, 'Объектно-ориентированное программирование'),
(1, 'Оперативное объединение программ'),
(1, 'Основные основы программирования'),
(1, 'Общее описание процессов'),
(2, '//'), (2, '<!-- -->'), (2, '#'), (2, '/* */'),
(3, 'list'), (3, 'dict'), (3, 'tuple'), (3, 'set'),
(4, 'input()'), (4, 'print()'), (4, 'output()'), (4, 'display()'),
(5, '21'), (5, '22'), (5, '80'), (5, '443');


