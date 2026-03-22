"""Stub for vxi11 (VXI-11 instrument control over Ethernet).

SDG6000X subclasses vxi11.Instrument, so we need a base class with
write / ask / close methods. All are no-ops in simulation.
"""


class Instrument:
    """Stub for vxi11.Instrument."""

    def __init__(self, host, name=None, client_id=None, term_char=None):
        self.host = host

    def write(self, message):
        pass

    def ask(self, message):
        return ""

    def read(self):
        return ""

    def close(self):
        pass

    def open(self):
        pass
