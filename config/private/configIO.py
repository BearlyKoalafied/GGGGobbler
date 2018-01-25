import configparser
import os
from util import filepather

FILENAME = "remote_config.ini"

def set_value(section, item, value):
    cfg = _read_ini()
    cfg.set(section, item, str(value))
    _write_out(cfg)

def get_boolean(section, item):
    cfg = _read_ini()
    return cfg.getboolean(section, item)

def get_int(section, item):
    cfg = _read_ini()
    return cfg.getint(section, item)

def _read_ini():
    cfg = configparser.ConfigParser()
    cfg.read(_get_filename())
    return cfg

def _write_out(cfg):
    with open(_get_filename(), 'w') as cfgfile:
        cfg.write(cfgfile)

def _get_filename():
    return filepather.relative_file_path(__file__, os.path.join(os.pardir, FILENAME))

_read_ini()
