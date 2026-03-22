"""sim/constraints.py — Physical operating constraints for FPGA output validation.

WHO SHOULD EDIT THIS FILE
    Only lab members with direct knowledge of the hardware operating ranges.
    Do not add a constraint unless you can cite a datasheet spec, a calibration
    result, or direct experimental knowledge.  Wrong constraints silently mask
    real problems or generate false warnings.

WHAT BELONGS HERE
    Per-device valid operating ranges that the sim should flag if violated.
    These are physical facts about the hardware, not software design choices.

WHAT DOES NOT BELONG HERE
    Display labels, system groupings, colours → sim/device_labels.py
    Stub behaviour, timing assumptions       → sim/stub_devices.py + SIM_ASSUMPTIONS.md

FORMAT
    DDS_CONSTRAINTS maps device_db key → constraint dict:
      valid_range_MHz : (min_MHz, max_MHz)  — flag any logged freq outside this range
      set_by          : "initials"          — who added this constraint
      source          : "citation"          — datasheet, calibration date, or experiment

    Leave DDS_CONSTRAINTS empty ({}) until a lab member fills it in.
    An empty dict means no validation is performed — the checksum still works.

RELATIONSHIP TO CHECKSUM
    sim/device_labels.checksum_events() hashes raw events only.
    Constraint warnings are displayed separately in the viewer and do NOT affect
    the checksum — the checksum is purely a fingerprint of FPGA output.

EXAMPLE (do not uncomment without verifying the numbers):

    DDS_CONSTRAINTS = {
        "urukul4_ch2": {
            "valid_range_MHz": (60, 120),
            "set_by": "JE",
            "source": "80 MHz AOM datasheet bandwidth spec, verified 2026-03-22",
        },
        "urukul4_ch1": {
            "valid_range_MHz": (320, 380),
            "set_by": "JK",
            "source": "imaging AOM calibration, 2025-11-10",
        },
    }
"""

DDS_CONSTRAINTS = {}
