import threading
import time
import datetime

from GGGGobbler.grabber import GGGGobblerBot
from db import db
from config import config, messages, settings
from GGGGobbler import goboauth, errorhandling
from log import gobblogger


def main():
    # connect using oauth to reddit
    reddit = goboauth.get_refreshable_instance()
    # setup logging
    gobblogger.prepare()
    start_threads(reddit)


def start_threads(reddit):
    praw_lock = threading.Lock()
    close_event = threading.Event()
    t_main = threading.Thread(group=None, target=thread_scan_reddit,
                              args=(reddit, close_event, praw_lock))
    t_messages = threading.Thread(group=None, target=thread_check_msgs,
                                  args=(reddit, close_event, praw_lock))
    t_close = threading.Thread(group=None, target=thread_wait_for_close,
                               args=(close_event,))
    t_main.start()
    t_messages.start()
    t_close.start()
    # manage_threads(reddit, retry_limit_event, close_event, praw_lock)


def manage_threads(r, retry_limit_event, close_event, praw_lock):
    while not close_event.is_set():
        if retry_limit_event.is_set():
            config.set_currently_running(False)
            errorhandling.send_error_mail(r, praw_lock, "Hit maximum retries with no solution, shutting down bot")
            retry_limit_event.clear()
        counter = secs_to_next_fraction_of_hour(config.wait_time_manager())
        while not close_event.is_set() and counter > 0:
            time.sleep(1)
            counter -= 1


def secs_to_next_fraction_of_hour(n):
    """
    :param n: number of seconds out of an hour to size a fraction
    :return: datetime
    """
    now = datetime.datetime.now()
    # number of seconds into the current hour
    cur_secs = now.second + now.minute * 60
    return (int(cur_secs / n) + 1) * n - cur_secs


def thread_scan_reddit(r, close_event, praw_lock):
    """
    This thread is responsible for monitoring reddit for forum posts, scraping pathofexile.com
    for staff posts, and creating corresponding reddit comments
    :param r: reddit praw intsance
    :param close_event: threading.Event to signal to this thread that we're closing the program
    :param praw_lock: threading.Lock to share the reddit instance
    """
    retry_count = config.retry_cap()
    retry_decrement_event = threading.Event()
    while not close_event.is_set():
        gobblogger.info("Starting run")
        dao = db.DAO()

        def func():
            bot = GGGGobblerBot(r, dao)
            bot.parse_reddit()
        # if we didn't trigger a retry last time, reset the count, otherwise clear the event
        if not retry_decrement_event.is_set():
            retry_count = config.retry_cap()
        else:
            retry_decrement_event.clear()
        if config.currently_running_enabled():
            errorhandling.handle_errors(r, praw_lock, dao, retry_count, retry_decrement_event,
                                        "Hit recoverable exception in main thread with " +
                                        str(retry_count) + " retries remaining: ",
                                        "Hit unexpected exception, stopping main thread: ", func)
        # if func threw a RECOVERABLE_EXCEPTIONS, decrement the retry counter by 1
        if retry_decrement_event.is_set():
            retry_count -= 1
        gobblogger.info("Finished run")
        counter = secs_to_next_fraction_of_hour(config.wait_time_main())
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
        errorhandling.handle_errors_check_messages(r, praw_lock,
                                                   "Hit recoverable exception in check messages thread: ",
                                                   "Hit unexpected exception in check messages thread: ",
                                                   messages.check_messages)
        counter = secs_to_next_fraction_of_hour(config.wait_time_check_messages())
        while not close_event.is_set() and counter > 0:
            time.sleep(1)
            counter -= 1

def thread_wait_for_close(close_event):
    s = input("Type Q to end: ")
    while s != "q" and s != "Q":
        s = input("Type Q to end: ")
    close_event.set()

if __name__ == "__main__":
    main()
