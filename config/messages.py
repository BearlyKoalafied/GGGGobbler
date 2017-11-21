from log import gobblogger
from config import config, settings

CFG_RESPONSE_MAIL_HEADER = "Config confirmed"
CFG_RESPONSE_MAIL_HEADER_FAIL = "Config failed!"

CFG_HELP = """
Commands help:

turn on/off - Controls running main thread (scanning and posting to reddit)

errmsg on/off - Controls whether to receive error notifications

waittime main/msgs/manager x - sets the waiting delay of each of the threads, should be a divisor of 3600

help - this info

"""

def check_messages(r):
    unread = r.inbox.unread()
    for new in unread:
        if new.author == settings.REDDIT_ACC_OWNER and new.subject == 'cfg':
            process(r, new.body)
            new.mark_read()


def process(r, body):
    split = body.split(' ')
    if body.startswith('turn on'):
        config.set_currently_running(True)
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Bot on')
        gobblogger.info("Received turn on config message")

    elif body.startswith('turn off'):
        config.set_currently_running(False)
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Bot off')
        gobblogger.info("Received turn off config message")

    elif body.startswith('errmsg on'):
        config.set_error_messaging(True)
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Error Messaging on')
        gobblogger.info("Received errmsg on config message")

    elif body.startswith('errmsg off'):
        config.set_error_messaging(False)
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                  'Turning Error Messaging off')
        gobblogger.info("Received errmsg off config message")

    elif len(split) == 3 and split[0] == 'waittime':
        confirm = split[1] == 'main' or split[1] == 'msgs' or split[1] == 'manager'
        if split[1] == 'main':
            config.set_wait_time_main(split[2])
        if split[1] == 'msgs':
            config.set_wait_time_check_messages(split[2])
        if split[1] == 'manager':
            config.set_wait_time_manager(split[2])
        if confirm:
            send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                      "Successfully configured waittime " + split[1] + " to " + str(split[2]))
            gobblogger.info("Received waittime config message")

    elif body.startswith('help'):
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, CFG_HELP)
        gobblogger.info("Received help request message")

def send_confirmation_message(reddit, header, body):
    reddit.redditor(settings.REDDIT_ACC_OWNER).message(header, body)
