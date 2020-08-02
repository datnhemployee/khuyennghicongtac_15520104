from datetime import datetime


def watch(func, *args, **kwargs):
    t1 = datetime.now()
    print("start:{0}".format(t1))
    result = func(*args, **kwargs)
    t2 = datetime.now()
    print("end:{0}".format(t2))
    seconds = (t2 - t1).total_seconds()
    print("seconds:{0}".format(seconds))
    return result


def get_current_time():
    import time
    return int(round(time.time() * 1000))
