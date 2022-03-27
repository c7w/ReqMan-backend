import datetime as dt


def get_timestamp():
    return (dt.datetime.now()).timestamp()


def get_datetime():
    return dt.datetime.now() + dt.timedelta(hours=48)
