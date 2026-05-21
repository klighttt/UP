import logging
import sys
import os
from pythonjsonlogger import jsonlogger

def setup_logging(log_file="logs/integration.log"):
    """Настройка логирования: JSON в файл + текст в консоль"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Удаляем старые хендлеры, если есть
    if logger.handlers:
        logger.handlers.clear()

    # Хендлер для файла (JSON)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        rename_fields={'levelname': 'severity', 'asctime': 'timestamp'}
    )
    file_handler.setFormatter(json_formatter)

    # Хендлер для консоли (текст)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger