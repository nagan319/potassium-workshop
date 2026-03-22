"""Simulation device database for POTASSIUM-WORKSHOP experiments.

Uses sim.stub_devices classes instead of real ARTIQ coredevices so experiments
can run on Linux without hardware. DDS entries preserve the fields that
waxx.control.artiq.DDS.read_db() reads at prepare() time:
  - AD9910: cpld_device, pll_n
  - CPLD:   spi_device, refclk
  - SPI:    channel
"""

_S = "sim.stub_devices"  # shorthand module name

device_db = {
    # ── Core ──────────────────────────────────────────────────────────────
    "core": {
        "type": "local",
        "module": _S,
        "class": "SimCore",
        "arguments": {},
    },
    "core_dma": {
        "type": "local",
        "module": _S,
        "class": "SimCoreDMA",
    },
    "core_cache": {
        "type": "local",
        "module": _S,
        "class": "SimCoreCache",
    },

    # ── I2C switches ──────────────────────────────────────────────────────
    "i2c_switch0": {
        "type": "local",
        "module": _S,
        "class": "SimI2CSwitch",
        "arguments": {"address": 0xe0},
    },
    "i2c_switch1": {
        "type": "local",
        "module": _S,
        "class": "SimI2CSwitch",
        "arguments": {"address": 0xe2},
    },
}

# ── Grabber ───────────────────────────────────────────────────────────────
device_db["grabber0"] = {
    "type": "local",
    "module": _S,
    "class": "SimGrabber",
    "arguments": {"channel_base": 0},
}

# ── Mirny (microwave source) ──────────────────────────────────────────────
device_db["spi_mirny0"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": 2},
}
for _sw in range(4):
    device_db[f"ttl_mirny0_sw{_sw}"] = {
        "type": "local",
        "module": _S,
        "class": "SimTTLOut",
        "arguments": {"channel": 3 + _sw},
    }
    device_db[f"mirny0_ch{_sw}"] = {
        "type": "local",
        "module": _S,
        "class": "SimADF5356",
        "arguments": {
            "channel": _sw,
            "sw_device": f"ttl_mirny0_sw{_sw}",
            "cpld_device": "mirny0_cpld",
        },
    }
device_db["mirny0_cpld"] = {
    "type": "local",
    "module": _S,
    "class": "SimMirny",
    "arguments": {
        "spi_device": "spi_mirny0",
        "refclk": 125000000.0,
        "clk_sel": "mmcx",
    },
}

# ── Urukul DDS (6 cards × 4 channels) ────────────────────────────────────
# channel numbering starts at 7 to match production db (value doesn't matter
# for stubs, but must be unique integers and present for read_db())
_ch_base = 7
for _i in range(6):
    _spi_name = f"spi_urukul{_i}"
    _cpld_name = f"urukul{_i}_cpld"
    _eeprom_name = f"eeprom_urukul{_i}"
    _io_upd = f"ttl_urukul{_i}_io_update"

    device_db[_eeprom_name] = {
        "type": "local",
        "module": _S,
        "class": "SimKasliEEPROM",
        "arguments": {"port": f"EEM{_i * 2 + 3}"},
    }
    device_db[_spi_name] = {
        "type": "local",
        "module": _S,
        "class": "SimSPIMaster",
        "arguments": {"channel": _ch_base},
    }
    _ch_base += 1
    device_db[_io_upd] = {
        "type": "local",
        "module": _S,
        "class": "SimTTLOut",
        "arguments": {"channel": _ch_base},
    }
    _ch_base += 1
    device_db[_cpld_name] = {
        "type": "local",
        "module": _S,
        "class": "SimUrukulCPLD",
        "arguments": {
            "spi_device": _spi_name,
            "sync_device": None,
            "io_update_device": _io_upd,
            "refclk": 125000000.0,
            "clk_sel": 2,
            "clk_div": 0,
        },
    }
    for _j in range(4):
        _sw_name = f"ttl_urukul{_i}_sw{_j}"
        device_db[_sw_name] = {
            "type": "local",
            "module": _S,
            "class": "SimTTLOut",
            "arguments": {"channel": _ch_base},
        }
        _ch_base += 1
        device_db[f"urukul{_i}_ch{_j}"] = {
            "type": "local",
            "module": _S,
            "class": "SimAD9910",
            "arguments": {
                "pll_n": 32,
                "pll_en": 1,
                "chip_select": 4 + _j,
                "cpld_device": _cpld_name,
                "sw_device": _sw_name,
            },
        }

# ── Sampler (ADC) ─────────────────────────────────────────────────────────
device_db["spi_sampler0_adc"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["spi_sampler0_pgia"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["ttl_sampler0_cnv"] = {
    "type": "local",
    "module": _S,
    "class": "SimTTLOut",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["sampler0"] = {
    "type": "local",
    "module": _S,
    "class": "SimSampler",
    "arguments": {
        "spi_adc_device": "spi_sampler0_adc",
        "spi_pgia_device": "spi_sampler0_pgia",
        "cnv_device": "ttl_sampler0_cnv",
    },
}

# ── Zotino (DAC) ──────────────────────────────────────────────────────────
device_db["spi_zotino0"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["ttl_zotino0_ldac"] = {
    "type": "local",
    "module": _S,
    "class": "SimTTLOut",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["ttl_zotino0_clr"] = {
    "type": "local",
    "module": _S,
    "class": "SimTTLOut",
    "arguments": {"channel": _ch_base},
}
_ch_base += 1
device_db["zotino0"] = {
    "type": "local",
    "module": _S,
    "class": "SimZotino",
    "arguments": {
        "spi_device": "spi_zotino0",
        "ldac_device": "ttl_zotino0_ldac",
        "clr_device": "ttl_zotino0_clr",
    },
}

# ── TTL channels 0-87 (from kexp/config/ttl_id.py) ────────────────────────
# ttl40 is the line_trigger (TTLInOut); all others are TTLOut.
for _n in range(88):
    if _n == 40:
        _cls = "SimTTLInOut"
    else:
        _cls = "SimTTLOut"
    device_db[f"ttl{_n}"] = {
        "type": "local",
        "module": _S,
        "class": _cls,
        "arguments": {"channel": 0x020000 + _n},
    }

# ── Shuttler ──────────────────────────────────────────────────────────────
device_db["shuttler0_led0"] = {
    "type": "local",
    "module": _S,
    "class": "SimTTLOut",
    "arguments": {"channel": 0x050000},
}
device_db["shuttler0_led1"] = {
    "type": "local",
    "module": _S,
    "class": "SimTTLOut",
    "arguments": {"channel": 0x050001},
}
device_db["shuttler0_config"] = {
    "type": "local",
    "module": _S,
    "class": "SimShuttlerConfig",
    "arguments": {"channel": 0x050002},
}
device_db["shuttler0_trigger"] = {
    "type": "local",
    "module": _S,
    "class": "SimShuttlerTrigger",
    "arguments": {"channel": 0x050003},
}
for _ch in range(16):
    device_db[f"shuttler0_dcbias{_ch}"] = {
        "type": "local",
        "module": _S,
        "class": "SimShuttlerDCBias",
        "arguments": {"channel": 0x050004 + _ch * 2},
    }
    device_db[f"shuttler0_dds{_ch}"] = {
        "type": "local",
        "module": _S,
        "class": "SimShuttlerDDS",
        "arguments": {"channel": 0x050005 + _ch * 2},
    }
device_db["shuttler0_spi0"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": 0x050024},
}
device_db["shuttler0_relay"] = {
    "type": "local",
    "module": _S,
    "class": "SimShuttlerRelay",
    "arguments": {"spi_device": "shuttler0_spi0"},
}
device_db["shuttler0_spi1"] = {
    "type": "local",
    "module": _S,
    "class": "SimSPIMaster",
    "arguments": {"channel": 0x050025},
}
device_db["shuttler0_adc"] = {
    "type": "local",
    "module": _S,
    "class": "SimShuttlerADC",
    "arguments": {"spi_device": "shuttler0_spi1"},
}
