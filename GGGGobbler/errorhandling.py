import threading
import traceback

from praw.exceptions import APIException, ClientException
from prawcore.exceptions import RequestException, ServerError

from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

from GGGGobbler import forum_parse as fparse
from config import config, settings
from log import gobblogger

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
    t_mail = threading.Thread(group=None, target=send_error_mail_thread,
                              args=(reddit, message, 5))
    t_mail.start()


def send_error_mail_thread(reddit, message, retry_count):
    try:
        reddit.redditor(settings.REDDIT_ACC_OWNER).message("Max retries reached", message)
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception("Hit recoverable exception while trying to send error message: ")
        t_mail = threading.Thread(group=None, target=send_error_mail_thread,
                                  args=(reddit, message, retry_count - 1))
        t_mail.start()
    except:
        gobblogger.exception("Hit unexpected exception while trying to send error message: ")
        raise


def handle_errors(reddit, dao, retry_count,
                  recoverable_err_msg, irrecoverable_err_msg,
                  func):
    try:
        func()
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception(recoverable_err_msg)
        # stop the main thread if we hit max retries
        if retry_count <= 0:
            gobblogger.exception("Ran out of retries while handling " + func.__name__ + ":")
            send_error_mail(reddit, "Hit maximum retries with no solution, shutting down bot. " +
                            "Last trackback: " + traceback.format_exc())
            config.set_currently_running(False)
        else:
            gobblogger.exception("Hit recoverable exception in main thread: ")
        if dao is not None:
            dao.rollback()
    except:
        gobblogger.exception(irrecoverable_err_msg)
        # stop the main thread from looping again
        config.set_currently_running(False)
        send_error_mail(reddit, "Hit maximum retries with no solution, shutting down bot. " +
                        "Last trackback: " + traceback.format_exc())
        if dao is not None:
            dao.rollback()
    finally:
        return retry_count


def handle_errors_check_messages(reddit, recoverable_err_msg, irrecoverable_err_msg, func):
    try:
        func(reddit)
    except RECOVERABLE_EXCEPTIONS:
        gobblogger.exception(recoverable_err_msg)
    except:
        gobblogger.exception(irrecoverable_err_msg)
        raise