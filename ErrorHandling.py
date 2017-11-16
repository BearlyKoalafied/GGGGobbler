import logging
import traceback

import forum_parse as fparse
import timeout
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
    try:
        reddit.redditor(settings.REDDIT_ACC_OWNER).message("Bot Crashed", message)
    except RECOVERABLE_EXCEPTIONS:
        logging.getLogger((settings.LOGGER_NAME).exception("Hit exception while sending error message: "))

def handle_errors(reddit, func, dao):
    try:
        func()
    except RECOVERABLE_EXCEPTIONS:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit Recoverable exception, output: ")
        dao.rollback()
    except timeout.TimeoutError:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit manual Timeout exception, output: ")
        send_error_mail(reddit, traceback.format_exc())
        dao.rollback()
    except:
        logging.getLogger(settings.LOGGER_NAME).exception("Hit Unexpected exception, output: ")
        send_error_mail(reddit, traceback.format_exc())
        dao.rollback()
        raise