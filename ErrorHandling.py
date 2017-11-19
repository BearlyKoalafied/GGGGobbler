import traceback
import threading
import functools

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


def send_error_mail(reddit, lock, message):
    """
    Attempt to send an error message to my main reddit account
    """
    t_mail = threading.Thread(group=None, target=send_error_mail_thread,
                              args=(reddit, lock, message, 5))
    t_mail.start()


def send_error_mail_thread(reddit, lock, message, retry_count):
    try:
        with lock:
            reddit.redditor(settings.REDDIT_ACC_OWNER).message("Max retries reached", message)
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception("Hit recoverable exception while trying to send error message: ")
        t_mail = threading.Thread(group=None, target=send_error_mail_thread,
                                  args=(reddit, lock, message, retry_count - 1))
        t_mail.start()
    except:
        gobblogger.exception("Hit unexpected exception while trying to send error message: ")
        raise
    finally:
        lock.release()

def handle_errors(reddit, lock, dao,
                  retry_count, retry_limit_event, retry_decrement_event,
                  recoverable_err_msg, irrecoverable_err_msg,
                  func, *args):
    try:
        lock.acquire()
        func(args)
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception(recoverable_err_msg)
        if retry_count == 0:
            gobblogger.exception("Ran out of retries while handling " + func.__name__ + ":")
            retry_limit_event.set()
            raise
        retry_decrement_event.set()
        dao.rollback()
    except:
        gobblogger.exception(irrecoverable_err_msg)
        dao.rollback()
        raise
    finally:
        lock.release()
