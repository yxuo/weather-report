import logging
import os


app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_logger(
        name: str,
        level=logging.DEBUG,
        log_to_file=True,
        log_to_stream=True,
        format_file=True,
        format_stream=True
):
    """Get logger with all needed configs"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s - %(message)s')

    if log_to_file:
        file_handler = logging.FileHandler(
            f'{app_folder}/log/report_generator.log')
        if format_file:
            file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    if log_to_stream:
        stream_handler = logging.StreamHandler()
        if format_stream:
            stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    return logger
