import logging
import sys

from celery.signals import after_setup_logger


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("api_errors.log")

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [console_handler, file_handler]


@after_setup_logger.connect
def setup_celery_logging(logger, **kwargs):
    logger.setLevel(logging.ERROR)
    logger.addHandler(file_handler)


celery_logger = logging.getLogger("celery")
celery_logger.addHandler(file_handler)
celery_logger.setLevel(logging.ERROR)
