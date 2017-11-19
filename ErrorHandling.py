import traceback
import threading

import forum_parse as fparse
import gobblogger
import settings

from praw.exceptions import APIException, ClientException
from prawcore.exceptions import RequestException, ServerError
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

RECOVERABLE_EXCEPTIONS = (APIException,
                          ClientException,
                          ConnectionError,
                          HTTPError,
                          ReadTimeout,
                          RequestException,
                          ServerError,
                          fparse.PathofexileDownException)

def send_error_mail(reddit, message):
    """
    Attempt to send an error message to my main reddit account
    """
    try:
        reddit.redditor(settings.REDDIT_ACC_OWNER).message("Bot Crashed", message)
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception("Hit exception while sending error message: ")
        raise
    except:
        gobblogger.exception("Hit Unexpected exception while sending error message: ")
        raise

def handle_err_send_error_mail_thread(reddit, message, lock, retry_count):
    try:
        with lock:
            send_error_mail(reddit, message)
    except RECOVERABLE_EXCEPTIONS:
        if retry_count == 0:
            gobblogger.exception("Ran out of retries while sending error message: ")
            raise
        # create threads trying to send mail until succession, or limit is reached
        thread = threading.Timer(15, handle_err_send_error_mail_thread, (reddit, message, retry_count - 1,))
        thread.start()
    finally:
        lock.release()

def handle_errors(reddit, func, dao, lock):
    try:
        lock.acquire()
        func()
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception("Hit Recoverable exception, output: ")
        dao.rollback()
    except:
        gobblogger.exception("Hit Unexpected exception, output: ")
        dao.rollback()
        handle_err_send_error_mail_thread(reddit, traceback.format_exc(), lock, 15)
        raise
    finally:
        lock.release()