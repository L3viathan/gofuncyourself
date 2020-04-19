from time import sleep

import pytest

from gofuncyourself import raise_after, gofunc


def test_raises():
    exc = raise_after(0.5, KeyError("wat"))
    with pytest.raises(KeyError):
        sleep(1)


def test_cancellable():
    exc = raise_after(1, KeyError("wat"))
    if exc:
        pass
    sleep(1.1)


def test_uncancellable():
    exc = raise_after(1, KeyError("wat"), allow_cancellation=False)
    if exc:
        pass
    with pytest.raises(KeyError):
        sleep(1.1)

def test_normal_usage():
    @gofunc(0.5)
    def do_work(fail=False):
        if fail:
            raise RuntimeError("noo")
        return "result"

    ret, exc = do_work()
    assert ret == "result"

    ret, exc = do_work(fail=True)
    assert ret is None
    with pytest.raises(RuntimeError):
        sleep(0.6)

    ret, exc = do_work(fail=True)
    assert ret is None
    if exc:
        assert "handled exception :)"
    sleep(0.6)

def test_magic_decorator():
    @gofunc
    def do_not_fail():
        return "Hello"

    ret, exc = do_not_fail()
    assert ret == "Hello"
