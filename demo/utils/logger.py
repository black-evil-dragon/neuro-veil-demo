from datetime import datetime
import logging


def setup_logger():
    """
    Настройка логгера с кодировкой UTF-8.
    """
    # Создаем логгер
    logger = logging.getLogger("neuro")
    logger.setLevel(logging.DEBUG)

    # Формат логов
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Логирование в файл с кодировкой UTF-8
    log_filename = f"./output/logs/neuro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(
        log_filename, encoding="utf-8"
    )  # Указываем кодировку UTF-8
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    logger = logging.getLogger("neuro")
    logger.setLevel(logging.DEBUG)

    return logger