import threading
import time
import datetime

from grabber import GGGGobblerBot
import db
import ErrorHandling
import msgcfg
import gobOauth
import gobblogger
import settings

def main():
    # connect using oauth to reddit
    reddit = gobOauth.get_refreshable_instance()
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
            msgcfg.set_currently_running(False)
            ErrorHandling.send_error_mail(r, praw_lock, "Hit maximum retries with no solution, shutting down bot")
            retry_limit_event.clear()
        counter = secs_to_next_fraction_of_hour(settings.WAIT_TIME_MANAGER)
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
    curSecs = now.second + now.minute * 60
    return (int(curSecs / n)+ 1)*n - curSecs

def thread_scan_reddit(r, close_event, praw_lock):
    """
    This thread is responsible for monitoring reddit for forum posts, scraping pathofexile.com
    for staff posts, and creating corresponding reddit comments
    :param r: reddit praw intsance
    :param close_event: threading.Event to signal to this thread that we're closing the program
    :param praw_lock: threading.Lock to share the reddit instance
    """
    retry_count = 8
    while not close_event.is_set():
        gobblogger.info("Starting run")
        dao = db.DAO()
        # run the bot
        def func():
            bot = GGGGobblerBot(r, dao)
            bot.parse_reddit()
        retry_decrement_event = threading.Event()

        if msgcfg.currently_running_enabled():
            ErrorHandling.handle_errors(r, praw_lock, dao, retry_count, retry_decrement_event,
                                    "Hit recoverable exception with " + str(retry_count) + " retries remaining: ",
                                    "Hit unexpected exception, stopping main thread: ", func)
        # if func threw a RECOVERABLE_EXCEPTIONS, decrement the retry counter by 1
        if retry_decrement_event.is_set():
            retry_count -= 1
        gobblogger.info("Finished run")
        counter = secs_to_next_fraction_of_hour(settings.WAIT_TIME_MAIN)
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
        counter = secs_to_next_fraction_of_hour(settings.WAIT_TIME_CHECK_MESSAGES)
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
