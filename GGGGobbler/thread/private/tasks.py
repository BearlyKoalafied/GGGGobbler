import traceback

from GGGGobbler.grabber import GGGGobblerBot
from db import db
from log import gobblogger
from config import config, messaging

def scan_reddit(r, retry_count):
    gobblogger.info("Starting run")
    dao = db.DAO()
    if config.currently_running_enabled():
        try:
            GGGGobblerBot(r, dao).parse_reddit()
        except:
            dao.rollback()
            gobblogger.exception("Fatal Error on main thread: ")
            messaging.send_response_message(r, "Fatal Error on main thread", traceback.format_exc())
            raise
    gobblogger.info("Finished run")
    return retry_count

def check_messages(r):
    try:
        messaging.scan_inbox(r)
    except:
        gobblogger.exception("Fatal Error on check messages thread: ")
        messaging.send_response_message(r, "Fatal Error on check messages thread", traceback.format_exc())
        raise
