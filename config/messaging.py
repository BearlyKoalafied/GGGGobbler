from log import gobblogger
from config import config, settings
from config.private import enum
from GGGGobbler import errorhandling

COMMANDS = {
    enum.CmndID.ACTIVATE: "turn",
    enum.CmndID.ERRMSG: "errmsg",
    enum.CmndID.WAITTIME: "waittime",
    enum.CmndID.HELP: "help",
    enum.CmndID.SHOWVALUES: "showvalues",
}

WAITTIME_OPTNS = {
    enum.WaittimeID.MAIN: 'main',
    enum.WaittimeID.MSGS: 'msgs',
}


CFG_RESPONSE_HEADER = "Config confirmed"
CFG_RESPONSE_HEADER_FAIL = "Config failed!"

CFG_HELP = """
Commands help:

turn on/off - Controls running main thread (scanning and posting to reddit)

errmsg on/off - Controls whether to receive error notifications

waittime main/msgs x - sets the waiting delay of each of the threads, should be a divisor of 3600

help - this info

"""

@errorhandling.RetryExceptions(errorhandling.RECOVERABLE_EXCEPTIONS, logger=gobblogger, retry_delay=5000, retry_backoff_multiplier=1.05)
def scan_inbox(r):
    unread = r.inbox.unread()
    for new in unread:
        if new.author == settings.REDDIT_ACC_OWNER and new.subject == "cfg":
            process(r, new.body.lower())
            new.mark_read()

def process(r, body):
    split = body.split(' ')
    if split[0] == COMMANDS[enum.CmndID.ACTIVATE]:
        if command_activate(split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Turning bot " + split[1])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    elif split[0] == COMMANDS[enum.CmndID.ERRMSG]:
        if command_errmsg(split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Turning Error Messaging " + split[1])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    elif split[0] == COMMANDS[enum.CmndID.WAITTIME]:
        if command_waittime(split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Setting wait time " + split[1] + " to " + split[2])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    # not parsing values for validity in these, just reading out information
    elif split[0] == COMMANDS[enum.CmndID.HELP]:
        send_response_message(r, CFG_RESPONSE_HEADER, CFG_HELP)
    elif split[0] == COMMANDS[enum.CmndID.SHOWVALUES]:
        output = "currently running: " + str(config.currently_running_enabled()) + "\n\n" \
               + "error msg enabled: " + str(config.error_messaging_enabled()) + "\n\n" \
               + "wait time main: " + str(config.wait_time_main()) + "\n\n" \
               + "wait time check messages: " + str(config.wait_time_check_messages()) + "\n\n" \
               + "retry cap: " + str(config.retry_cap()) + "\n\n"
        send_response_message(r, CFG_RESPONSE_HEADER, output)
    else:
        send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Not a valid command - type 'help' for information")
        gobblogger.info("Received invalid config command: " + body)
        return
    gobblogger.info("Received config command: " + body)

def command_activate(split):
    # test if the passes command qualifies as valid
    if len(split) != 2:
        return False
    value = split[1]
    # test the value qualifies
    if not passes_value_rules(enum.CmndID.ERRMSG, value):
        return False
    config.set_currently_running(value)
    return True

def command_errmsg(split):
    # test if the passed command qualifies as valid
    if len(split) != 2:
        return False
    value = split[1]
    # test if the value qualifies
    if not passes_value_rules(enum.CmndID.ERRMSG, value):
        return False
    config.set_error_messaging(value)
    return True

def command_waittime(split):
    # test if the passed command qualifies as valid
    if len(split) != 3:
        return False
    option = split[1]
    value = split[2]
    # test if the value qualifies
    if not passes_value_rules(enum.CmndID.WAITTIME, value):
        return False
    if option == WAITTIME_OPTNS[enum.WaittimeID.MAIN]:
        config.set_wait_time_main(value)
    elif option == WAITTIME_OPTNS[enum.WaittimeID.MSGS]:
        config.set_wait_time_check_messages(value)
    else:
        return False
    return True

def passes_value_rules(commandID, value):
    if commandID == enum.CmndID.ACTIVATE or commandID == enum.CmndID.ERRMSG:
        return value == 'on' or value == 'off' or value == 'true' or value == 'false'
    elif commandID == enum.CmndID.WAITTIME:
        if not value.isdigit():
            return False
        if 3600 % int(value) != 0:
            return False
        if int(value) <= 0:
            return True
    return False

@errorhandling.RetryExceptions(errorhandling.RECOVERABLE_EXCEPTIONS, logger=gobblogger, retry_limit=20, retry_delay=5000)
def send_response_message(reddit, header, body):
    reddit.redditor(name=settings.REDDIT_ACC_OWNER).message(header, body)
