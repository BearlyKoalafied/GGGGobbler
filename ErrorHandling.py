import logging
import traceback
import time

import forum_parse as fparse
import timeout
import msgcfg
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
    Returns False on failure due to network errors
    """
    try:
        reddit.redditor(settings.REDDIT_ACC_OWNER).message("Bot Crashed", message)
        return True
    except RECOVERABLE_EXCEPTIONS:
        logging.getLogger((settings.LOGGER_NAME).exception("Hit exception while sending error message: "))
        return False
    except:
        logging.getLogger((settings.LOGGER_NAME).exception("Hit Unexpected exception while sending error message: "))

def handle_errors(reddit, func, dao):
    try:
        func()
    except RECOVERABLE_EXCEPTIONS:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit Recoverable exception, output: ")
        dao.rollback()
    except timeout.TimeoutError:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit manual Timeout exception, output: ")
        dao.rollback()
        if msgcfg.error_messaging_enabled():
            while not send_error_mail(reddit, traceback.format_exc()):
                time.sleep(60000)
    except:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit Unexpected exception, output: ")
        dao.rollback()
        if msgcfg.error_messaging_enabled():
            while not send_error_mail(reddit, traceback.format_exc()):
                time.sleep(60000)
        raise