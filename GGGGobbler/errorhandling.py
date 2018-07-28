import logging
import time
import functools
import traceback

from praw.exceptions import APIException, ClientException
from prawcore.exceptions import RequestException, ResponseException, ServerError
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout
from GGGGobbler.forum_parse import PathofexileDownException

RECOVERABLE_EXCEPTIONS = (APIException,
                          ClientException,
                          ConnectionError,
                          HTTPError,
                          ReadTimeout,
                          RequestException,
                          ResponseException,
                          ServerError,
                          PathofexileDownException)

class DefaultLogger:
    def log(self, level, msg):
        print(msg)

class RetryExceptions:
    def __init__(self, exceptions, logger=DefaultLogger(), log_level=logging.ERROR,
                retry_delay=1000, retry_backoff_multiplier=1, retry_limit=None):
        self.exceptions = exceptions
        self.logger = logger
        self.log_level = log_level
        self.retry_delay = retry_delay
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.retry_limit = retry_limit
        self.retries_remaining = retry_limit

    def __call__(self, func):
        @functools.wraps(func)
        def retry(*args, **kwargs):
            backoff_generator = self.growing_backoff(self.retry_delay, self.retry_backoff_multiplier)
            try:
                # if no retry limit was specified, we'll just go infinitely
                while self.retry_limit is None or self.retries_remaining > 0:
                    try:
                        return func(*args, **kwargs)
                    except self.exceptions as e:
                        self.recoverable_handle(backoff_generator, e)
                    except Exception as e:
                        self.irrecoverable_handle(e)
                        raise
                    if self.retries_remaining is not None:
                        self.retries_remaining -= 1
            finally:
                self.retries_remaining = self.retry_limit
            return func(*args, **kwargs)
        return retry

    def recoverable_handle(self, backoff_generator, e):
        # if we're using a retry limit, specify remaining retries in the log message
        if self.retry_limit:
            msg = "Recoverable Exception caught with {} retries remaining:\n {}"\
                .format(self.retries_remaining, traceback.format_exc())
        else:
            msg = "Recoverable Exception {} caught".format(traceback.format_exc())
        self.logger.log(self.log_level, msg)
        time.sleep(self.retry_delay)
        # grow the backoff
        self.retry_delay = next(backoff_generator)

    def irrecoverable_handle(self, e):
        msg = "Unexpected Exception {}".format(traceback.format_exc())
        self.logger.log(self.log_level, msg)

    def growing_backoff(self, delay, backoff):
        while True:
            delay *= backoff
            yield delay
