from GGGGobbler.grabber import GGGGobblerBot
from GGGGobbler import errorhandling
from db import db
from log import gobblogger
from config import config, messaging

def scan_reddit(r, retry_count):
    gobblogger.info("Starting run")
    dao = db.DAO()
    if config.currently_running_enabled():
        GGGGobblerBot(r, dao).parse_reddit()
    gobblogger.info("Finished run")
    return retry_count

def check_messages(r):
    messaging.scan_inbox(r)
