import praw
import configparser
import settings

CFG_FILE = "remote_config.ini"

CFG_RESPONSE_MAIL_HEADER = "Config confirmed"
CFG_RESPONSE_MAIL_HEADER_FAIL = "Config failed!"

def read_ini():
    cfg = configparser.ConfigParser()
    cfg.read(CFG_FILE)
    return cfg

def check_messages(r):
    unread = r.get_unread()
    for new in unread:
        if new.author == settings.REDDIT_ACC_OWNER:
            process(r, new.body)

def process(r, body):
    if body.startsWith('turn on'):
        set_currently_running('on')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                    'Turning Bot on')

    elif body.startsWith('turn off'):
        set_currently_running('off')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                    'Turning Bot off')

    elif body.startsWith('errmsg on'):
        set_error_messaging('on')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                    'Turning Error Messaging on')

    elif body.startsWith('errmsg off'):
        set_error_messaging('off')
        send_confirmation_message(r, CFG_RESPONSE_MAIL_HEADER,
                                    'Turning Error Messaging off')


def send_confirmation_message(reddit, header, body):
    reddit.redditor(settings.REDDIT_ACC_OWNER).message(header, body)

def set_currently_running(new_setting):
    cfg = read_ini()
    cfg['currently_running'] = new_setting

def set_error_messaging(new_setting):
    cfg = read_ini()
    cfg['error_reddit_messaging'] = new_setting

def currently_running_enabled():
    cfg = read_ini()
    if cfg['currently_running'] == 'on':
        return True
    else:
        return False

def error_messaging_enabled():
    cfg = read_ini()
    if cfg['error_reddit_messaging'] == 'on':
        return True
    else:
        return False
