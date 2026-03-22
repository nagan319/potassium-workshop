"""Simulation stub devices for ARTIQ hardware.

These are drop-in replacements for real ARTIQ coredevices. All kernel methods
are no-ops that run as plain Python in artiq.sim simulation mode.

Used via sim/device_db.py with artiq.sim.devices.Core as the core device.
"""

from artiq.sim.devices import Core as _SimCore


class SimCore(_SimCore):
    """artiq.sim.devices.Core extended with reset() and break_realtime()."""

    def __init__(self, dmgr, **kwargs):
        super().__init__(dmgr)

    def reset(self):
        pass

    def break_realtime(self):
        pass


class SimCoreDMA:
    class _DMAContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def record(self, name):
        return self._DMAContext()

    def erase(self, name):
        pass

    def get_handle(self, name):
        return 0

    def playback(self, name):
        pass

    def playback_mu(self, handle):
        pass


class SimCoreCache:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")
        self._store = {}

    def get(self, key):
        return self._store.get(key, [])

    def put(self, key, value):
        self._store[key] = value


class SimTTLOut:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def on(self):
        pass

    def off(self):
        pass

    def set_o(self, value):
        pass

    def pulse(self, duration):
        pass

    def pulse_mu(self, duration_mu):
        pass


class SimTTLInOut(SimTTLOut):
    def input(self):
        pass

    def output(self):
        pass

    def set_oe(self, oe):
        pass

    def gate_rising(self, duration):
        pass

    def gate_falling(self, duration):
        pass

    def gate_both(self, duration):
        pass

    def count(self, up_to_timestamp_mu):
        return 0

    def timestamp_mu(self, up_to_timestamp_mu):
        return 0


class SimSPIMaster:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def set_config(self, flags, length, freq, cs):
        pass

    def set_config_mu(self, flags, length, div, cs):
        pass

    def write(self, data):
        pass

    def read(self):
        return 0


class SimUrukulCPLD:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def init(self):
        pass

    def set_sync_div(self, div):
        pass

    def set_att(self, channel, att):
        pass

    def set_att_mu(self, channel, att_mu):
        pass

    def get_att_mu(self):
        return 0

    def cfg_sw(self, channel, on):
        pass

    def cfg_reg(self, reg):
        pass


class _SimTTLSwitch:
    """TTL-like switch attached as the .sw attribute of SimAD9910."""

    def on(self):
        pass

    def off(self):
        pass


class SimAD9910:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")
        self.sw = _SimTTLSwitch()

    def init(self):
        pass

    def set(self, frequency=0., phase=0., amplitude=0., phase_mode=-1,
            ref_time_mu=-1, profile=0):
        pass

    def set_mu(self, frequency, phase=0, amplitude=0, profile=0,
               phase_mode=-1, ref_time_mu=-1):
        pass

    def set_att(self, att):
        pass

    def set_att_mu(self, att_mu):
        pass

    def get_att_mu(self):
        return 0

    def set_phase_mode(self, phase_mode):
        pass

    def write32(self, addr, data):
        pass

    def write64(self, addr, data_high, data_low):
        pass

    def cfg_sw(self, state):
        pass

    def get(self, profile=0):
        return (0., 0., 0.)


class SimZotino:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def init(self):
        pass

    def write_dac(self, channel, voltage):
        pass

    def write_dac_mu(self, channel, value):
        pass

    def set_dac(self, voltages, channels=None):
        pass

    def set_dac_mu(self, values, channels=None):
        pass

    def load(self):
        pass

    def read_reg(self, addr):
        return 0


class SimSampler:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def init(self):
        pass

    def sample(self, buf):
        pass

    def sample_mu(self, buf):
        pass

    def set_gain_mu(self, channel, gain):
        pass

    def get_gains(self):
        return 0


class SimKasliEEPROM:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")


class SimMirny:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def init(self):
        pass

    def set_att(self, channel, att):
        pass

    def set_att_mu(self, channel, att_mu):
        pass

    def write_reg(self, addr, data):
        pass

    def read_reg(self, addr):
        return 0


class SimADF5356:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def init(self):
        pass

    def set_frequency(self, frequency):
        pass

    def set_output_power(self, rf_power, mux_out=0):
        pass


class SimI2CSwitch:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def set(self, channel):
        pass

    def unset(self, channel):
        pass


class SimGrabber:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def input(self):
        pass


class SimShuttlerConfig:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def set_config(self, en, limit, i_dds=0):
        pass


class SimShuttlerRelay:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def enable(self, en_word):
        pass

    def init(self):
        pass


class SimShuttlerTrigger:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def trigger(self, trig_out):
        pass


class SimShuttlerDCBias:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def set_waveform(self, b0, b1, b2, b3):
        pass

    def smooth_mu(self, start, stop, duration_mu, order):
        pass


class SimShuttlerDDS:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def set_waveform(self, a0, a1, a2, a3, f0, f1, p0):
        pass


class SimShuttlerADC:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")

    def read_raw(self):
        return [0] * 8

    def read_volt(self):
        return [0.0] * 8
