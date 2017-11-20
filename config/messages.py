from log import gobblogger
from config import config, settings

CFG_RESPONSE_MAIL_HEADER = "Config confirmed"
CFG_RESPONSE_MAIL_HEADER_FAIL = "Config failed!"


def check_messages(r):
    unread = r.inbox.unread()
    for new in unread:
        if new.author == settings.REDDIT_ACC_OWNER:
            process(r, new.body)
        new.mark_read()


def process(r, body):
    split = body.split(' ')
    if body.startswith('turn on'):
        config.set_currently_running('on')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Bot on')
        gobblogger.info("Received turn on config message")

    elif body.startswith('turn off'):
        config.set_currently_running('off')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Bot off')
        gobblogger.info("Received turn off config message")

    elif body.startswith('errmsg on'):
        config.set_error_messaging('on')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER, 'Turning Error Messaging on')
        gobblogger.info("Received errmsg on config message")

    elif body.startswith('errmsg off'):
        config.set_error_messaging('off')
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

def send_confirmation_message(reddit, header, body):
    reddit.redditor(settings.REDDIT_ACC_OWNER).message(header, body)
