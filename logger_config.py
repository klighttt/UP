# logger_config.py
import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging(log_file="logs/system.log"):
    # Создаём директорию для логов, если её нет
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Хендлер для файла (JSON)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s %(module)s %(funcName)s',
        rename_fields={'levelname': 'severity', 'asctime': 'timestamp'}
    )
    file_handler.setFormatter(json_formatter)

    # Хендлер для консоли (простой текст)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger