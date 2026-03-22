"""Stub for artiq.coredevice.shuttler (added in ARTIQ 8).

Provides no-op stand-ins for DCBias, DDS, Relay, Trigger, Config, and
shuttler_volt_to_mu so that waxx.control.artiq.Shuttler_CH can be imported
in simulation mode without a real Shuttler card or ARTIQ 8 codebase.
"""


class DCBias:
    """Stub for artiq.coredevice.shuttler.DCBias."""

    def __init__(self, dmgr, channel, core_device="core"):
        self.core = dmgr.get(core_device)

    def set_waveform(self, b0=0, b1=0, b2=0, b3=0):
        pass

    def smooth_mu(self, start, stop, duration_mu, order):
        pass


class DDS:
    """Stub for artiq.coredevice.shuttler.DDS."""

    def __init__(self, dmgr, channel, core_device="core"):
        self.core = dmgr.get(core_device)

    def set_waveform(self, b0=0, b1=0, b2=0, b3=0, c0=0, c1=0, c2=0):
        pass


class Relay:
    """Stub for artiq.coredevice.shuttler.Relay."""

    def __init__(self, dmgr, spi_device, core_device="core"):
        self.core = dmgr.get(core_device)

    def init(self):
        pass

    def enable(self, en=0):
        pass


class Trigger:
    """Stub for artiq.coredevice.shuttler.Trigger."""

    def __init__(self, dmgr, channel, core_device="core"):
        self.core = dmgr.get(core_device)

    def trigger(self, trig_out=0):
        pass


class Config:
    """Stub for artiq.coredevice.shuttler.Config."""

    def __init__(self, dmgr, channel, core_device="core"):
        self.core = dmgr.get(core_device)

    def set_config(self, en=0, limit=0, i_dds=0):
        pass


def shuttler_volt_to_mu(volt):
    """Convert voltage to Shuttler machine unit (stub returns 0)."""
    return 0
