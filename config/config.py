import configparser

from config.private import configIO


def set_currently_running(new_setting):
    configIO.set_value('features', 'currently_running', new_setting)

def set_error_messaging(new_setting):
    configIO.set_value('features', 'error_messaging_enabled', new_setting)

def set_wait_time_main(new_setting):
    configIO.set_value('thread_delays', 'wait_time_main', new_setting)

def set_wait_time_check_messages(new_setting):
    configIO.set_value('thread_delays', 'wait_time_check_messages', new_setting)

def set_wait_time_manager(new_setting):
    configIO.set_value('thread_delays', 'set_wait_time_manager', new_setting)

def currently_running_enabled():
    return configIO.get_boolean('features', 'currently_running')

def error_messaging_enabled():
    return configIO.get_boolean('features', 'error_messaging_enabled')

def wait_time_main():
    return configIO.get_int('thread_delays', 'wait_time_main')

def wait_time_check_messages():
    return configIO.get_int('thread_delays', 'wait_time_check_messages')

def wait_time_manager():
    return configIO.get_int('thread_delays', 'wait_time_manager')
