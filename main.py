import threading
import functools
import time
import logging


from grabber import GGGGobblerBot
import db
import ErrorHandling
import msgcfg
import gobOauth
import settings

def main():
    # connect using oauth to reddit
    reddit = gobOauth.get_refreshable_instance()
    # setup logging
    logger = logging.getLogger(settings.LOGGER_NAME)
    fh = logging.FileHandler(settings.LOGFILE_NAME)
    fmt = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    if not settings.LOGGING_ON:
        logging.disable(logging.CRITICAL)
    start_main_threads(reddit)

def start_main_threads(reddit):
    praw_lock = threading.Lock()
    close_event = threading.Event()
    t_scan_reddit = threading.Timer(10, thread_scan_reddit, (reddit, close_event, praw_lock))
    t_messages = threading.Timer(0, thread_check_msgs, (reddit, close_event, praw_lock))
    t_scan_reddit.start()
    t_messages.start()
    try:
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:
        close_event.set()
        raise

def thread_scan_reddit(r, close_event, praw_lock):
    """
    This thread is responsible for monitoring reddit for forum posts and creating
    corresponding reddit comments
    :param r: reddit praw intsance
    :param close_event: threading.Event to signal to this thread that we're closing the program
    :param praw_lock: threading.Lock to share the reddit instance
    """
    while not close_event.is_set():
        logging.getLogger(settings.LOGGER_NAME).info("Starting run")
        dao = db.DAO()
        # run the bot
        def func():
            if msgcfg.currently_running_enabled():
                bot = GGGGobblerBot(r, dao)
                bot.parse_reddit()
        # managing exceptions
        ErrorHandling.handle_errors(r, func, dao, praw_lock)
        logging.getLogger(settings.LOGGER_NAME).info("Finished run")
        counter = settings.WAIT_TIME_MAIN
        while not close_event.is_set() and counter > 0:
            time.sleep(1)
            counter -= 1

def thread_check_msgs(r, close_event, praw_lock):
    """
    This thread is responsible for monitoring the bot's message inbox and performing tasks
    related to that
    :param r: reddit praw intsance
    :param close_event: threading.Event to signal to this thread that we're closing the program
    :param praw_lock: threading.Lock to share the reddit instance
    """
    while not close_event.is_set():
        with praw_lock:
            msgcfg.check_messages(r)
        counter = settings.WAIT_TIME_CHECK_MESSAGES
        while not close_event.is_set() and counter > 0:
            time.sleep(1)
            counter -= 1

if __name__ == "__main__":
    main()
