import logging
import settings

def prepare():
    logger = logging.getLogger(settings.LOGGER_NAME)
    fh = logging.FileHandler(settings.LOGFILE_NAME)
    fmt = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    if not settings.LOGGING_ON:
        logging.disable(logging.CRITICAL)

def info(message):
    logging.getLogger(settings.LOGGER_NAME).info(message)

def exception(message):
    logging.getLogger(settings.LOGGER_NAME).exception(message)
