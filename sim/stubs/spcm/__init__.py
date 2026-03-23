"""Simulation stub for spcm (Spectrum Instrumentation AWG driver).

The real spcm package loads libspcm_linux.so at import time and raises an
exception if the hardware driver is absent.  This stub replaces it for
simulation runs.

units is a real pint.UnitRegistry — same definition as the real spcm — so
unit arithmetic (50 * units.ohm, 0.428 * units.V, …) works correctly.
All hardware classes (Card, DDSCommandList, Channels, Trigger, …) are no-ops.
Integer constants mirror the real spcm constant names so code referencing them
doesn't NameError.
"""

import numpy as np
from pint import UnitRegistry

from .classes_error_exception import SpcmException, SpcmError, SpcmTimeout

# ── Real pint unit registry (identical to real spcm) ─────────────────────────
units = UnitRegistry(autoconvert_offset_to_baseunit=True)
units.define("sample = 1 = Sa = Sample = Samples = S")
units.define("promille = 0.001 = ‰ = permille = perthousand = perthousands = ppt")
units.define("fraction = 1 = frac = Frac = Fracs = Fraction = Fractions = Frac = Fracs")
units.highZ = np.inf * units.ohm

# ── Integer constants (values are arbitrary for simulation) ───────────────────
SPC_REP_STD_DDS             = 0x00400000
SPC_TMASK_EXT0              = 0x00000002
SPC_TM_POS                  = 0x00000001
COUPLING_DC                 = 1
SPCM_DDS_TRG_SRC_CARD       = 0
SPCM_DDS_TRG_SRC_TIMER      = 1
SPCM_DDS_DTM_DMA            = 1
SPCM_DDS_CORE0              = 0x00000001
SPCM_DDS_CORE1              = 0x00000002
SPCM_DDS_CORE2              = 0x00000004
SPCM_DDS_CORE3              = 0x00000008
SPCM_DDS_CORE4              = 0x00000010
SPCM_DDS_CORE5              = 0x00000020
SPCM_DDS_CORE6              = 0x00000040
SPCM_DDS_CORE7              = 0x00000080
SPCM_DDS_CORE8              = 0x00000100
SPCM_DDS_CORE9              = 0x00000200
SPCM_DDS_CORE10             = 0x00000400
SPCM_DDS_CORE11             = 0x00000800
M2CMD_CARD_ENABLETRIGGER    = 0x00000100
M2CMD_CARD_START            = 0x00000040
M2CMD_CARD_STOP             = 0x00000200


# ── Hardware stub classes ─────────────────────────────────────────────────────

class _DDSChannel:
    """Single DDS core — stub; all calls are no-ops."""
    def amp(self, value):   pass
    def freq(self, value):  pass
    def phase(self, value): pass


class DDSCommandList:
    """Stub for spcm.DDSCommandList.

    avail_freq_slope_step / avail_amp_slope_step return 0 so the
    minimum-step enforcement in TweezerTrap.compute_slopes() never clips
    any computed slope.
    """

    class WRITE_MODE:
        WAIT_IF_FULL = 0

    def __init__(self, card=None):
        self._channels = [_DDSChannel() for _ in range(20)]
        self.mode = self.WRITE_MODE.WAIT_IF_FULL

    def __getitem__(self, idx):
        return self._channels[idx]

    def reset(self):                            pass
    def data_transfer_mode(self, mode):         pass
    def trg_src(self, src):                     pass
    def trg_timer(self, dt):                    pass
    def exec_at_trg(self):                      pass
    def write(self):                            pass
    def write_to_card(self):                    pass
    def cores_on_channel(self, ch, *cores):     pass

    def freq(self, idx, value):                 pass
    def freq_slope(self, idx, value):           pass
    def amp(self, idx, value):                  pass
    def amp_slope(self, idx, value):            pass

    def avail_freq_slope_step(self) -> float:   return 0.0
    def avail_amp_slope_step(self) -> float:    return 0.0


class Card:
    def __init__(self, ip=None):    pass
    def open(self, ip=None):        pass
    def reset(self):                pass
    def card_mode(self, mode):      pass
    def write_setup(self):          pass
    def start(self, flags=0):       pass
    def stop(self):                 pass
    def close(self):                pass


class Channels:
    def __init__(self, card=None):      pass
    def enable(self, on=True):          pass
    def output_load(self, value):       pass
    def amp(self, value):               pass


class Trigger:
    def __init__(self, card=None):          pass
    def or_mask(self, mask):               pass
    def ext0_mode(self, mode):             pass
    def ext0_level0(self, level):          pass
    def ext0_coupling(self, coupling):     pass
