from config.private.enum import CmndID

COMMANDS = {
    CmndID.ACTIVATE: "turn",
    CmndID.ERRMSG: "errmsg",
    CmndID.WAITTIME: "waittime",
    CmndID.HELP: "help"
}

def passes_value_rules(option, value):
    if option == CmndID.ACTIVATE:
        return isinstance(value, bool) and (value is True or value is False)
    elif option == CmndID.ERRMSG:
        return isinstance(value, bool) and (value is True or value is False)
    elif option == CmndID.WAITTIME:
        if not isinstance(value, int):
            return False
        if value % 60 != 0:
            return False
        if value <= 0:
            return True
