"""sim/device_labels.py — Functional name and system-group mappings for all FPGA devices.

SOURCES (every field is traceable to one of these files — no guesses):
  k-exp/kexp/config/ttl_id.py      — TTL channel numbers and functional names
  k-exp/kexp/config/dds_id.py      — DDS urukul assignments, default frequencies
  k-exp/kexp/config/expt_params.py — Physical transition frequencies

This file contains:
  - Name/channel mappings    (sourced from k-exp)
  - Default frequencies      (sourced from k-exp)
  - System groupings         (viewer display only — cosmetic, not physics)
  - Display colours          (viewer display only — cosmetic, not physics)

This file does NOT contain:
  - Valid frequency ranges   → see sim/constraints.py (domain-expert-set, empty by default)
  - Validation logic         → see sim/constraints.py
  - Checksums                → checksum is over raw events only (see sim/device_labels.checksum_events)

--- HOW TO ADAPT FOR A NEW EXPERIMENT ---
Change `system` groupings and ordering here to reorganise the viewer panels.
Everything else (valid ranges, physical bounds) goes in sim/constraints.py.
"""

import hashlib
import json

# ── Raman physics constants ────────────────────────────────────────────────────
# Source: kexp/config/expt_params.py — self.p.frequency_raman_transition
RAMAN_TRANSITION_FREQ_HZ = 147.2583e6   # Hz  (≈ 147.26 MHz, used in raman_pulse_test.py)

# ── TTL label map ─────────────────────────────────────────────────────────────
# Source: kexp/config/ttl_id.py
# Each entry: {"name": str, "system": str}
# system must appear in TTL_SYSTEM_ORDER (or it lands in "Other")

TTL_LABELS = {
    "ttl0":  {"name": "outer_coil_discharge_igbt",   "system": "Coil"},
    "ttl1":  {"name": "tweezer_pid2_enable",          "system": "Tweezer"},
    "ttl2":  {"name": "inner_coil_pid",               "system": "Coil"},
    "ttl3":  {"name": "outer_coil_pid",               "system": "Coil"},
    "ttl4":  {"name": "lightsheet_sw",                "system": "Tweezer"},
    "ttl5":  {"name": "basler",                       "system": "Imaging"},
    "ttl6":  {"name": "inner_coil_igbt",              "system": "Coil"},
    "ttl7":  {"name": "andor",                        "system": "Imaging"},
    "ttl8":  {"name": "outer_coil_igbt",              "system": "Coil"},
    "ttl9":  {"name": "hbridge_helmholtz",            "system": "Coil"},
    "ttl10": {"name": "z_basler",                     "system": "Imaging"},
    "ttl11": {"name": "tweezer_pid1_int_hold_zero",   "system": "Tweezer"},
    "ttl12": {"name": "lightsheet_pid_int_hold_zero", "system": "Tweezer"},
    "ttl13": {"name": "aod_rf_sw",                    "system": "Tweezer"},
    "ttl14": {"name": "awg_trigger",                  "system": "Trigger"},
    "ttl15": {"name": "zshim_hbridge_flip",           "system": "Coil"},
    "ttl16": {"name": "pd_scope_trig",                "system": "Trigger"},
    "ttl17": {"name": "pd_scope_trig_2",              "system": "Trigger"},
    "ttl18": {"name": "imaging_shutter_xy",           "system": "Imaging"},
    "ttl19": {"name": "imaging_shutter_x",            "system": "Imaging"},
    "ttl20": {"name": "basler_2dmot",                 "system": "Imaging"},
    "ttl21": {"name": "test_trig",                    "system": "Trigger"},
    "ttl22": {"name": "raman_shutter",                "system": "Raman"},
    "ttl24": {"name": "pd_scope_trig3",               "system": "Trigger"},
    "ttl36": {"name": "integrator_int_hold",          "system": "Coil"},
    "ttl38": {"name": "integrator_reset",             "system": "Coil"},
    "ttl40": {"name": "line_trigger",                 "system": "Trigger"},
    "ttl48": {"name": "keithley_trigger",             "system": "Trigger"},
    "ttl49": {"name": "imaging_pid_int_clear_hold",   "system": "Imaging"},
    "ttl50": {"name": "b_field_stab_SRS_blanking",    "system": "Coil"},
    "ttl51": {"name": "imaging_pid_manual_override",  "system": "Imaging"},
    "ttl52": {"name": "ry_980_sw",                    "system": "Laser"},
    "ttl53": {"name": "phase_lock_beam_enable",       "system": "Laser"},
    "ttl55": {"name": "test_2",                       "system": "Trigger"},
    "ttl56": {"name": "z_shim_pid_int_hold_zero",     "system": "Coil"},
}

TTL_SYSTEM_ORDER = ["Raman", "Imaging", "Coil", "Tweezer", "Laser", "Trigger"]

TTL_SYSTEM_COLORS = {
    "Raman":   "#f96",
    "Imaging": "#4af",
    "Coil":    "#f66",
    "Tweezer": "#8f8",
    "Laser":   "#c8f",
    "Trigger": "#888",
    "Other":   "#aaa",
}

# ── DDS label map ─────────────────────────────────────────────────────────────
# Source: kexp/config/dds_id.py
#
# Each entry:
#   name             : functional name — source: dds_id.py attribute name
#   system           : viewer display group (cosmetic only, not physics)
#   default_freq_MHz : value of default_freq= argument in dds_id.py, or None for
#                      detuning-based channels where no fixed AO frequency is set

DDS_LABELS = {
    # source: dds_id.py line 52  self.antenna_rf    = self.dds_assign(0,0, default_freq=200.e6)
    "urukul0_ch0": {"name": "antenna_rf",        "system": "RF",      "default_freq_MHz": 200.0},
    # source: dds_id.py line 55  self.tweezer_pid_1 = self.dds_assign(0,3, default_freq=80.e6)
    "urukul0_ch3": {"name": "tweezer_pid_1",     "system": "Tweezer", "default_freq_MHz":  80.0},
    # source: dds_id.py line 59  self.tweezer_pid_2 = self.dds_assign(1,0, default_freq=200.e6)
    "urukul1_ch0": {"name": "tweezer_pid_2",     "system": "Tweezer", "default_freq_MHz": 200.0},
    # source: dds_id.py line 63  self.ry_405_sw     = self.dds_assign(1,1, default_freq=287.4e6)
    "urukul1_ch1": {"name": "ry_405_sw",         "system": "Laser",   "default_freq_MHz": 287.4},
    # source: dds_id.py line 68  self.d2_3d_c       = self.dds_assign(1,2, default_detuning=...)
    "urukul1_ch2": {"name": "d2_3d_c",           "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 71  self.d2_3d_r       = self.dds_assign(1,3, default_detuning=...)
    "urukul1_ch3": {"name": "d2_3d_r",           "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 75  self.push          = self.dds_assign(2,0, default_detuning=...)
    "urukul2_ch0": {"name": "push",              "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 78  self.d2_2dv_r      = self.dds_assign(2,1, default_detuning=...)
    "urukul2_ch1": {"name": "d2_2dv_r",          "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 81  self.d2_2dv_c      = self.dds_assign(2,2, default_detuning=...)
    "urukul2_ch2": {"name": "d2_2dv_c",          "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 84  self.d2_2dh_r      = self.dds_assign(2,3, default_detuning=...)
    "urukul2_ch3": {"name": "d2_2dh_r",          "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 88  self.d2_2dh_c      = self.dds_assign(3,0, default_detuning=...)
    "urukul3_ch0": {"name": "d2_2dh_c",          "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 91  self.mot_killer    = self.dds_assign(3,1, default_detuning=...)
    "urukul3_ch1": {"name": "mot_killer",         "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 94  self.beatlock_ref  = self.dds_assign(3,2, default_freq=42.26e6)
    "urukul3_ch2": {"name": "beatlock_ref",       "system": "RF",      "default_freq_MHz":  42.26},
    # source: dds_id.py line 97  self.d1_3d_c       = self.dds_assign(3,3, default_detuning=...)
    "urukul3_ch3": {"name": "d1_3d_c",           "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 102 self.d1_3d_r       = self.dds_assign(4,0, default_detuning=...)
    "urukul4_ch0": {"name": "d1_3d_r",           "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 106 self.imaging       = self.dds_assign(4,1, default_freq=350.e6)
    "urukul4_ch1": {"name": "imaging",            "system": "Imaging", "default_freq_MHz": 350.0},
    # source: dds_id.py line 110 self.raman_80_plus = self.dds_assign(4,2, default_freq=80.e6)
    "urukul4_ch2": {"name": "raman_80_plus",      "system": "Raman",   "default_freq_MHz":  80.0},
    # source: dds_id.py line 113 self.optical_pumping = self.dds_assign(4,3, default_detuning=...)
    "urukul4_ch3": {"name": "optical_pumping",    "system": "Cooling", "default_freq_MHz": None},
    # source: dds_id.py line 117 self.raman_150_minus = self.dds_assign(5,0, default_freq=150.e6)
    "urukul5_ch0": {"name": "raman_150_minus",    "system": "Raman",   "default_freq_MHz": 150.0},
    # source: dds_id.py line 121 self.raman_switch  = self.dds_assign(5,1, default_freq=150.0e6)
    "urukul5_ch1": {"name": "raman_switch",       "system": "Raman",   "default_freq_MHz": 150.0},
    # source: dds_id.py line 124 self.imaging_x_switch = self.dds_assign(5,2, default_freq=100.e6)
    "urukul5_ch2": {"name": "imaging_x_switch",   "system": "Imaging", "default_freq_MHz": 100.0},
    # source: dds_id.py line 128 self.raman_150_plus = self.dds_assign(5,3, default_freq=150.e6)
    "urukul5_ch3": {"name": "raman_150_plus",     "system": "Raman",   "default_freq_MHz": 150.0},
}

DDS_SYSTEM_ORDER = ["Raman", "Imaging", "Cooling", "Tweezer", "Laser", "RF"]

DDS_SYSTEM_COLORS = {
    "Raman":   "#f96",
    "Imaging": "#4af",
    "Cooling": "#66f",
    "Tweezer": "#8f8",
    "Laser":   "#c8f",
    "RF":      "#fa4",
    "Other":   "#aaa",
}

# ── Convenience sets ──────────────────────────────────────────────────────────
RAMAN_DDS_DEVICES = {k for k, v in DDS_LABELS.items() if v["system"] == "Raman"}
RAMAN_TTL_DEVICES = {k for k, v in TTL_LABELS.items() if v["system"] == "Raman"}


# ── Checksum ──────────────────────────────────────────────────────────────────

def checksum_events(events):
    """SHA-256 of the raw hardware event log only.

    The hash is a function of what the FPGA received — frequencies, amplitudes,
    voltages, TTL states, and their timestamps.  It does NOT depend on:
      - device_labels.py (cosmetic mappings)
      - sim/constraints.py (manual validation bounds)
      - any other sim configuration

    This makes the checksum a stable, reproducible fingerprint of the experiment
    output independent of how the sim or viewer is configured.

    Canonical form: events sorted by (t_mu, device, event) so that insertion
    order does not affect the hash.
    """
    canonical = json.dumps(
        sorted(events, key=lambda e: (e.get("t_mu", 0), e.get("device", ""), e.get("event", ""))),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


# ── API payload ───────────────────────────────────────────────────────────────

def api_labels_payload():
    """Full dict served at /api/labels — all viewer config in one place."""
    return {
        "ttl":               TTL_LABELS,
        "dds":               DDS_LABELS,
        "ttl_system_order":  TTL_SYSTEM_ORDER,
        "dds_system_order":  DDS_SYSTEM_ORDER,
        "ttl_system_colors": TTL_SYSTEM_COLORS,
        "dds_system_colors": DDS_SYSTEM_COLORS,
    }
