from config.private.enum import CmndID

COMMANDS = {
    CmndID.ACTIVATE: "turn",
    CmndID.ERRMSG: "errmsg",
    CmndID.WAITTIME: "waittime",
    CmndID.HELP: "help"
}

def passes_value_rules(option, value):
    if option == CmndID.ACTIVATE or option == CmndID.ERRMSG:
        return value == 'on' or value == 'off' or value == 'true'  or value == 'false'
    elif option == CmndID.WAITTIME:
        if not isinstance(value, int):
            return False
        if 3600 % value != 0:
            return False
        if value <= 0:
            return True
