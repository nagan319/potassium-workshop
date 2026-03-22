"""Stub for pylablib.core.utils.general."""


class Countdown:
    def __init__(self, timeout=None):
        self._timeout = timeout

    def passed(self):
        return False

    def time_left(self):
        return self._timeout if self._timeout else float("inf")
