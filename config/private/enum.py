import enum

class CmndID(enum.Enum):
    ACTIVATE = 1
    ERRMSG = 2
    WAITTIME = 3
    HELP = 4
    SHOWVALUES = 5

class WaittimeID(enum.Enum):
    MAIN = 1
    MSGS = 2
