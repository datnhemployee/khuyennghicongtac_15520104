from threading import Thread


def promise(**kwargs):
    result = {"has_error": True,
              "message": "The function has not been excuted yet."}
    try:
        task = kwargs.get("task")
        callback = kwargs.get("callback", None)
        on_error = kwargs.get("on_error", None)
        args = kwargs.get("args", {})
        result = task(**args)

        if (result is None):
            result = {}
    except ValueError as err:
        print("error", err)
        if (on_error is not None):
            on_error(err)
        return

    if (callback is not None):
        callback(**result)


def excute(**kwargs):
    Thread(target=promise, kwargs=kwargs).start()
