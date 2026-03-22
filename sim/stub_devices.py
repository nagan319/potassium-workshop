"""Simulation stub devices for ARTIQ hardware.

These are drop-in replacements for real ARTIQ coredevices. All kernel methods
are no-ops that run as plain Python in artiq.sim simulation mode.

Used via sim/device_db.py with artiq.sim.devices.Core as the core device.

State logging
-------------
SimAD9910 and SimTTLOut log every meaningful state change to _sim_log so you
can see a "preview" of what the hardware would be doing.  Print the log with:
    from sim.stub_devices import print_sim_log; print_sim_log()
or it is printed automatically at experiment end if SIM_LOG=1 is set.
"""

import os
from artiq.sim.devices import Core as _SimCore

# ── Simulation state log ─────────────────────────────────────────────────────
# Each entry is a flat dict with t_mu as an integer nanosecond timestamp
# (1 MU = 1 ns, matching hardware with ref_period = 1e-9 s).
#
# event types and their fields:
#   TTL  "state"    — state: "ON" | "OFF"
#   TTL  "pulse"    — duration_mu: int (ns)
#   DDS  "set"      — freq_MHz: float, amp: float, phase_turns: float
#   DDS  "att"      — att_dB: float
#   DAC  "write"    — channel: int, voltage: float
#
# Print:  from sim.stub_devices import print_sim_log; print_sim_log()
# Save:   from sim.stub_devices import save_sim_log; save_sim_log(path)
# Load:   import pandas as pd; df = pd.read_json(path, lines=True)
# Plot:   df[df.device=="urukul5_ch3"].plot(x="t_mu", y="freq_MHz")
# Hash:   hashlib.sha256(open(path,"rb").read()).hexdigest()

_sim_log = []


def _log_event(device, event, **fields):
    """Append one timestamped hardware event to _sim_log (t_mu in nanoseconds)."""
    try:
        from artiq.language.core import now_mu
        t_mu = int(now_mu())
    except Exception:
        t_mu = 0
    _sim_log.append({"t_mu": t_mu, "device": device, "event": event, **fields})


def print_sim_log():
    """Print hardware event log in [MU] DEVICE EVENT VALUE format."""
    if not _sim_log:
        print("[sim] No hardware events recorded.")
        return
    print(f"\n[sim] Hardware event log ({len(_sim_log)} events)  (1 MU = 1 ns):")
    for entry in _sim_log:
        t_mu = entry["t_mu"]
        name = entry["device"]
        evt  = entry["event"]
        vals = " ".join(f"{k}={v}" for k, v in entry.items()
                        if k not in ("t_mu", "device", "event"))
        print(f"[{t_mu:>16d}] {name:<32} {evt:<10} {vals}")
    print()


def save_sim_log(path):
    """Write _sim_log to a JSON Lines file.

    Format: one JSON object per line, t_mu is integer nanoseconds.
    Compatible with pd.read_json(path, lines=True) and hashlib checksumming.
    """
    import json
    with open(path, "w") as f:
        for entry in _sim_log:
            f.write(json.dumps(entry) + "\n")


class SimCore(_SimCore):
    """artiq.sim.devices.Core with the full timing API used by k-exp/waxx.

    Overrides run() to handle kernel_from_string()-generated kernels, where
    artiq_embedded.function is a source-code string rather than a callable
    (the ARTIQ compiler reads the string; the sim path must exec() it first).
    """

    def __init__(self, dmgr, **kwargs):
        super().__init__(dmgr)
        # Hardware-accurate machine unit: 1 MU = 1 ns (125 MHz RTIO clock).
        # sitecustomize.py patches artiq.language.core.delay() to convert
        # seconds → integer nanoseconds before feeding the MU counter, so
        # delay() and delay_mu() use the same scale.
        self.ref_period = 1e-9

    def run(self, k_function, k_args, k_kwargs):
        fn = k_function.artiq_embedded.function
        if isinstance(fn, str):
            # kernel_from_string stores source code for the compiler.
            # Re-exec it to get a real callable for simulation.
            ctx = {}
            exec(fn, ctx)
            real_fn = ctx["kernel_from_string_fn"]
            return real_fn(*k_args, **k_kwargs)
        # Call parent run() but suppress the artiq.sim timeline printout —
        # it's noisy and redundant with our own _sim_log.
        self._level += 1
        r = k_function.artiq_embedded.function(*k_args, **k_kwargs)
        self._level -= 1
        return r

    def reset(self):
        pass

    def break_realtime(self):
        pass

    def wait_until_mu(self, cursor_mu):
        pass

    def get_rtio_counter_mu(self):
        return 0

    def mu_to_seconds(self, mu):
        return mu * self.ref_period

    def seconds_to_mu(self, seconds):
        import numpy as np
        return np.int64(seconds // self.ref_period)


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
        self._name = kwargs.get("_sim_name", "ttl?")
        self._state = 0

    def on(self):
        if self._state != 1:
            self._state = 1
            _log_event(self._name, "state", state="ON")

    def off(self):
        if self._state != 0:
            self._state = 0
            _log_event(self._name, "state", state="OFF")

    def set_o(self, value):
        if value:
            self.on()
        else:
            self.off()

    def pulse(self, duration):
        _log_event(self._name, "pulse", duration_s=duration)

    def pulse_mu(self, duration_mu):
        _log_event(self._name, "pulse_mu", duration_mu=int(duration_mu))


class SimTTLInOut(SimTTLOut):
    """TTL input/output stub.

    Simulates an always-ready input (e.g. line trigger that fires immediately):
      - gate_rising / gate_falling / gate_both open a gate and return the
        current sim time + a 1 ps offset so the value is > 0.
      - timestamp_mu returns that offset once (gate open → event detected),
        then returns -1 on every subsequent call (no more events).
    This lets wait_for_line_trigger exit on the first try and
    clear_input_events exit on the first try.
    """

    def __init__(self, dmgr, **kwargs):
        super().__init__(dmgr, **kwargs)
        self._gate_open = False

    def input(self):
        pass

    def output(self):
        pass

    def set_oe(self, oe):
        pass

    def _open_gate(self, duration):
        self._gate_open = True
        from artiq.language.core import now_mu
        return now_mu() + 1   # 1 MU = 1 ns offset; always > 0

    def gate_rising(self, duration):
        return self._open_gate(duration)

    def gate_falling(self, duration):
        return self._open_gate(duration)

    def gate_both(self, duration):
        return self._open_gate(duration)

    def count(self, up_to_timestamp_mu):
        return 0

    def timestamp_mu(self, up_to_timestamp_mu):
        if self._gate_open:
            self._gate_open = False
            from artiq.language.core import now_mu
            return now_mu() + 1   # 1 MU = 1 ns; > 0 → wait_for_line_trigger exits
        return -1                  # no more events → clear_input_events exits


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
        self._name = kwargs.get("_sim_name", "cpld?")

    def init(self):
        pass

    def set_sync_div(self, div):
        pass

    def set_att(self, channel, att):
        # att in dB (float); log per-channel attenuation setting
        _log_event(self._name, "att", channel=int(channel), att_dB=round(float(att), 3))

    def set_att_mu(self, channel, att_mu):
        # att_mu: 8-bit value; 0 = 31.5 dB, 255 = 0 dB, step = 0.5 dB/LSB
        att_dB = round((255 - int(att_mu)) / 2.0, 1)
        _log_event(self._name, "att", channel=int(channel), att_dB=att_dB, att_mu=int(att_mu))

    def get_att_mu(self):
        return 0

    def cfg_sw(self, channel, on):
        pass

    def cfg_reg(self, reg):
        pass


class _SimTTLSwitch:
    """TTL-like RF switch attached as the .sw attribute of SimAD9910."""

    def __init__(self, dds_name="dds?"):
        self._name = dds_name + ".sw"
        self._state = 0

    def on(self):
        if self._state != 1:
            self._state = 1
            _log_event(self._name, "state", state="ON")

    def off(self):
        if self._state != 0:
            self._state = 0
            _log_event(self._name, "state", state="OFF")


class SimAD9910:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")
        self._name = kwargs.get("_sim_name", "dds?")
        self.sw = _SimTTLSwitch(self._name)
        self._freq = 0.
        self._amp = 0.
        self._phase = 0.

    def init(self):
        pass

    def set(self, frequency=0., phase=0., amplitude=0., phase_mode=-1,
            ref_time_mu=-1, profile=0):
        changed = (frequency != self._freq or amplitude != self._amp
                   or phase != self._phase)
        if changed:
            self._freq = frequency
            self._amp = amplitude
            self._phase = phase
            _log_event(self._name, "set",
                       freq_MHz=round(frequency / 1e6, 6),
                       amp=round(amplitude, 6),
                       phase_turns=round(phase, 6))

    def set_mu(self, frequency, phase=0, amplitude=0, profile=0,
               phase_mode=-1, ref_time_mu=-1):
        pass

    def set_att(self, att):
        # att in dB (float)
        _log_event(self._name, "att", att_dB=round(float(att), 3))

    def set_att_mu(self, att_mu):
        # att_mu: 8-bit; 0 = 31.5 dB, 255 = 0 dB, step = 0.5 dB/LSB
        att_dB = round((255 - int(att_mu)) / 2.0, 1)
        _log_event(self._name, "att", att_dB=att_dB, att_mu=int(att_mu))

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
        return (self._freq, self._phase, self._amp)


class SimZotino:
    def __init__(self, dmgr, **kwargs):
        self.core = dmgr.get("core")
        self._name = kwargs.get("_sim_name", "zotino?")

    def init(self):
        pass

    def write_dac(self, channel, voltage):
        _log_event(self._name, "write", channel=int(channel), voltage=round(float(voltage), 6))

    def write_dac_mu(self, channel, value):
        # 16-bit value; Zotino vref = 10 V, range 0 – 0xFFFF → −10 V to +10 V
        voltage = round((int(value) / 0xFFFF) * 20.0 - 10.0, 6)
        _log_event(self._name, "write", channel=int(channel), voltage=voltage, value_mu=int(value))

    def set_dac(self, voltages, channels=None):
        for i, v in enumerate(voltages):
            ch = channels[i] if channels is not None else i
            _log_event(self._name, "write", channel=int(ch), voltage=round(float(v), 6))

    def set_dac_mu(self, values, channels=None):
        for i, val in enumerate(values):
            ch = channels[i] if channels is not None else i
            voltage = round((int(val) / 0xFFFF) * 20.0 - 10.0, 6)
            _log_event(self._name, "write", channel=int(ch), voltage=voltage, value_mu=int(val))

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
        self._name = kwargs.get("_sim_name", "mirny?")

    def init(self):
        pass

    def set_att(self, channel, att):
        _log_event(self._name, "att", channel=int(channel), att_dB=round(float(att), 3))

    def set_att_mu(self, channel, att_mu):
        att_dB = round((255 - int(att_mu)) / 2.0, 1)
        _log_event(self._name, "att", channel=int(channel), att_dB=att_dB, att_mu=int(att_mu))

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
