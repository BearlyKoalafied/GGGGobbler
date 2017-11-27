from GGGGobbler.grabber import GGGGobblerBot
from GGGGobbler import errorhandling
from db import db
from log import gobblogger
from config import config, messaging

def scan_reddit(r, retry_count):
    gobblogger.info("Starting run")
    dao = db.DAO()
    if config.currently_running_enabled():
        retry_count = errorhandling.handle_errors(r, dao, retry_count,
                                    "Hit recoverable exception in main thread with " +
                                    str(retry_count) + " retries remaining: ",
                                    "Hit unexpected exception, stopping main thread: ",
                                    GGGGobblerBot(r, dao).parse_reddit)
    gobblogger.info("Finished run")
    return retry_count

def check_messages(r):
    errorhandling.handle_errors_check_messages(r, "Hit recoverable exception in check messages task: ",
                                               "Hit unexpected exception in check messages thread: ",
                                               messaging.scan_inbox)
