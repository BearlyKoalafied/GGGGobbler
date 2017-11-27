import datetime

def secs_to_next_fraction_of_hour(n):
    """
    :param n: number of seconds out of an hour to size a fraction
    :return: datetime
    """
    now = datetime.datetime.now()
    # number of seconds into the current hour
    cur_secs = now.second + now.minute * 60
    return (int(cur_secs / n) + 1) * n - cur_secs