import configparser

from util import filepather

def set_value(section, item, value):
    global cfg
    cfg.set(section, item, str(value))
    _write_out(cfg)

def get_boolean(section, item):
    global cfg
    cfg.getboolean(section, item)

def get_int(section, item):
    global cfg
    cfg.getint(section, item)

def _read_ini():
    global cfg
    cfg = configparser.ConfigParser()
    cfg.read(_get_filename())
    return cfg

def _write_out(cfg):
    with open(_get_filename(), 'w') as cfgfile:
        cfg.write(cfgfile)

def _get_filename():
    return filepather.relative_file_path(__file__, '../remote_config.ini')
