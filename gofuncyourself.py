import ctypes
import threading
from time import sleep
from random import random
from functools import wraps

DEFAULT_DELAY = 1


def ctype_async_raise(thread_obj, exception):
    # adapted from https://gist.github.com/liuw/2407154
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        raise ValueError("Invalid thread object")

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(target_tid), ctypes.py_object(exception)
    )
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ParentAwareThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.parent = threading.current_thread()
        super().__init__(*args, **kwargs)


ACTIVE_DELAYED_EXCEPTIONS = {}
CURRENT_EXCEPTION_ID = None


class DelayedException(Exception):
    def __init__(self):
        global CURRENT_EXCEPTION_ID
        exception = ACTIVE_DELAYED_EXCEPTIONS.pop(CURRENT_EXCEPTION_ID)
        CURRENT_EXCEPTION_ID = None
        raise exception from None


def make_cancellable(exception):
    def cancel():
        global ACTIVE_DELAYED_EXCEPTION
        ACTIVE_DELAYED_EXCEPTION = None

    setattr(exception, "cancel", cancel)


class ExceptionWrapper:
    def __init__(self, key=None, exception=None):
        self.key = key
        self.exception = exception

    def cancel(self):
        ACTIVE_DELAYED_EXCEPTIONS.pop(self.key)

    def __bool__(self):
        if self.key:
            self.cancel()
        return bool(self.exception)


def raise_after(n, exception, allow_cancellation=True):
    def worker(n, key):
        global CURRENT_EXCEPTION_ID
        sleep(n)
        if key in ACTIVE_DELAYED_EXCEPTIONS or key is None:
            CURRENT_EXCEPTION_ID = key
            ctype_async_raise(threading.current_thread().parent, DelayedException)

    key = random() if allow_cancellation else None
    ACTIVE_DELAYED_EXCEPTIONS[key] = exception
    ParentAwareThread(target=worker, args=[n, key]).start()
    return ExceptionWrapper(key, exception)


def gofunc(delay=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ret, exc = None, None
            try:
                ret = fn(*args, **kwargs)
            except Exception as e:
                exc = raise_after(delay, e)
            return ret, exc

        return wrapper

    if callable(delay):
        fn = delay
        delay = DEFAULT_DELAY
        return decorator(fn)
    return decorator
