import enum

class CmndID(enum.Enum):
    ACTIVATE = 1
    ERRMSG = 2
    WAITTIME = 3

class WaittimeID(enum.Enum):
    MAIN = 1
    MSGS = 2