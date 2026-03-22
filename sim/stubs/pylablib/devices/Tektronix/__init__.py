"""Stub for pylablib.devices.Tektronix — satisfies ITektronixScope import.

TektronixTBS1104B_Base subclasses ITektronixScope; all methods are no-ops.
"""


class ITektronixScope:
    """Stub base class for Tektronix oscilloscope drivers."""

    def __init__(self, device_id=None, **kwargs):
        self.device_id = device_id

    def close(self):
        pass

    def write(self, message):
        pass

    def ask(self, message):
        return ""

    def query(self, message):
        return ""

    def read(self):
        return ""

    def grab_single(self, channel=1, timeout=None):
        import numpy as np
        return np.zeros((2, 1))

    def get_waveform(self, channel=1):
        import numpy as np
        return np.zeros((2, 1))
