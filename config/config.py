import configparser

from util import filepather

def read_ini():
    cfg = configparser.ConfigParser()
    cfg.read(_get_filename())
    return cfg

def set_currently_running(new_setting):
    cfg = read_ini()
    cfg.set('features', 'currently_running', str(new_setting))
    _write_out(cfg)

def set_error_messaging(new_setting):
    cfg = read_ini()
    cfg.set('features', 'error_reddit_messaging', str(new_setting))
    _write_out(cfg)

def set_wait_time_main(new_setting):
    cfg = read_ini()
    cfg.set('thread_delays', 'wait_time_main', str(new_setting))
    _write_out(cfg)

def set_wait_time_check_messages(new_setting):
    cfg = read_ini()
    cfg.set('thread_delays', 'wait_time_check_messages', str(new_setting))
    _write_out(cfg)

def set_wait_time_manager(new_setting):
    cfg = read_ini()
    cfg.set('thread_delays', 'wait_time_manager', str(new_setting))
    _write_out(cfg)

def currently_running_enabled():
    cfg = read_ini()
    return cfg.getboolean('features', 'currently_running')

def error_messaging_enabled():
    cfg = read_ini()
    return cfg.getboolean('features', 'error_messaging_enabled')

def wait_time_main():
    cfg = read_ini()
    return cfg.getint('thread_delays', 'wait_time_main')

def wait_time_check_messages():
    cfg = read_ini()
    return cfg.getint('thread_delays', 'wait_time_check_messages')

def wait_time_manager():
    cfg = read_ini()
    return cfg.getint('thread_delays', 'wait_time_manager')

def _write_out(cfg):
    with open(_get_filename(), 'w') as cfgfile:
        cfg.write(cfgfile)

def _get_filename():
    return filepather.relative_file_path(__file__, 'remote_config.ini')
