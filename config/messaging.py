from log import gobblogger
from config import config, settings
from config.private import enum

COMMANDS = {
    enum.CmndID.ACTIVATE: "turn",
    enum.CmndID.ERRMSG: "errmsg",
    enum.CmndID.WAITTIME: "waittime",
    enum.CmndID.HELP: "help",
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

def scan_inbox(r):
    unread = r.inbox.unread()
    for new in unread:
        if new.author == settings.REDDIT_ACC_OWNER and new.subject == "cfg":
            process(r, new.body.lower())
            new.mark_read()

def process(r, body):
    split = body.split(' ')
    if split[0] == COMMANDS[enum.CmndID.ACTIVATE]:
        if command_activate(r, split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Turning bot " + split[1])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    elif split[0] == COMMANDS[enum.CmndID.ERRMSG]:
        if command_errmsg(r, split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Turning Error Messaging " + split[1])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    elif split[0] == COMMANDS[enum.CmndID.WAITTIME]:
        if command_waittime(r, split):
            send_response_message(r, CFG_RESPONSE_HEADER, "Setting wait time " + split[1] + " to " + split[2])
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Failed to read command: " + body)
            gobblogger.info("Received invalid config command: " + body)
    elif split[0] == COMMANDS[enum.CmndID.HELP]:
        if command_help(r, split):
            send_response_message(r, CFG_RESPONSE_HEADER, CFG_HELP)
        else:
            send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Help command failed")
            gobblogger.info("Received invalid config command: " + body)
    else:
        send_response_message(r, CFG_RESPONSE_HEADER_FAIL, "Not a valid command - type 'help' for information")
        gobblogger.info("Received invalid config command: " + body)
        return
    gobblogger.info("Received config command: " + body)

def command_activate(r, split):
    # test if the passes command qualifies as valid
    if len(split) != 2:
        return False
    value = split[1]
    # test the value qualifies
    if not passes_value_rules(enum.CmndID.ERRMSG, value):
        return False
    config.set_currently_running(value)
    return True

def command_errmsg(r, split):
    # test if the passed command qualifies as valid
    if len(split) != 2:
        return False
    value = split[1]
    # test if the value qualifies
    if not passes_value_rules(enum.CmndID.ERRMSG, value):
        return False
    config.set_error_messaging(value)
    return True

def command_waittime(r, split):
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

def command_help(r, split):
    # we don't care much about qualifying here, just the above check if the first term is 'help' will do
    # including this function anyway for consistency
    return True

def passes_value_rules(commandID, value):
    if commandID == enum.CmndID.ACTIVATE or commandID == enum.CmndID.ERRMSG:
        return value == 'on' or value == 'off' or value == 'true' or value == 'false'
    elif commandID == enum.CmndID.WAITTIME:
        if not isinstance(value, int):
            return False
        if 3600 % value != 0:
            return False
        if value <= 0:
            return True

def send_response_message(reddit, header, body):
    reddit.redditor(settings.REDDIT_ACC_OWNER).message(header, body)
