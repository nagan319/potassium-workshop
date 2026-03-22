# SIM_ASSUMPTIONS.md

Assumptions made by the simulation HAL (`sim/stub_devices.py`, `sim/stubs/`, `sitecustomize.py`).
Each entry names the assumption, its effect on experiment logic, and how to verify it.

---

## ARTIQ runtime

| Assumption | Effect | Check |
|---|---|---|
| `@kernel` methods on objects without `self.core` (DDS/TTL wrappers) run as plain Python | All waxx/kexp control-layer kernels execute; timing is not enforced | Any wrapper class kernel that has real sequencing implications may silently succeed |
| `delay()` is patched in `sitecustomize.py` to convert seconds → integer nanoseconds before advancing the MU counter | `delay(1e-3)` and `delay_mu(1_000_000)` both advance the clock by 1,000,000 MU (1 ms); the two APIs are consistent | Patch must load before any artiq import; verify with `import artiq.language.core; artiq.language.core.delay.__module__` — should not be `artiq.language.core` |
| `SimCore.ref_period = 1e-9` (1 MU = 1 ns, 125 MHz RTIO clock) | `seconds_to_mu(1e-3) = 1_000_000`; all log timestamps are in integer nanoseconds | |
| `at_mu()` with a past timestamp raises `ValueError: Attempted to go back in time` | Use `delay(-dt)` for backward offsets; `at_mu` can only advance | |
| `kernel_from_string` source strings are `exec()`'d and called directly | Kernels generated at runtime (e.g. scan loops) execute correctly | The `exec()` context has no access to the caller's local scope; only globals injected at exec time are visible |

---

## TTL outputs (`SimTTLOut`)

| Assumption | Effect | Check |
|---|---|---|
| `on()` / `off()` are no-ops if state is already correct | Sim log reflects only actual state changes | Redundant on/off pairs (e.g. double-off) are silently ignored |
| `pulse(duration)` logs the requested duration but does not advance the sim clock | Pulse duration is recorded but not cross-checked against timing constraints | Real minimum pulse-width violations will not be caught |

---

## TTL input (`SimTTLInOut`, used for `ttl40` / line trigger)

| Assumption | Effect | Check |
|---|---|---|
| Every `gate_rising` / `gate_falling` / `gate_both` call immediately produces one event | `wait_for_line_trigger` always exits on the first gate; power-line phase at the time of any experiment step is **not modeled** | Any experiment whose physics depends on triggering relative to the 60 Hz line phase is not faithfully reproduced |
| `timestamp_mu` returns `-1` after the gate-event is consumed | `clear_input_events` exits on the first call | If an experiment calls `clear_input_events` with an open gate (no prior `wait_for_line_trigger`), it will consume the phantom event and still exit cleanly |
| Returned timestamps are `now_mu() + 1e-12` (1 ps in sim units) | `at_mu(t_edge)` advances the clock by 1 ps; subsequent `delay(T_LINE_TRIGGER_RTIO_DELAY)` adds 100 µs as intended | The 1 ps is a numerical artefact with no physical meaning |

---

## DDS — AD9910 (`SimAD9910`)

| Assumption | Effect | Check |
|---|---|---|
| `set()` is a pure state-update + log; no SPI transfer, no PLL relock delay | Frequency changes appear instantaneous in sim | Experiments sensitive to PLL relock time (~1 ms on real hardware) will see no transient |
| `set_mu()` is a no-op (does not update internal state) | Only the float-argument `set()` path is tracked; raw-register writes are invisible | Any code path that uses `set_mu()` will not appear in the sim log |
| RF switch (`sw.on()` / `sw.off()`) is instantaneous | Switch timing is not enforced | Experiments relying on switch-on delay or isolation specs are not validated |
| `set_att(att_dB)` and `set_att_mu(att_mu)` are logged | Per-channel attenuator state is tracked | ✓ |
| `set_att_mu` conversion: `att_dB = (255 − att_mu) / 2` | Matches AD9910 datasheet (0.5 dB/LSB, 0 = 31.5 dB, 255 = 0 dB) | Verify against actual urukul configuration if attenuation precision matters |

---

## DDS — waxx `DDS` wrapper (`raman_150_plus`, etc.)

| Assumption | Effect | Check |
|---|---|---|
| `dds_minus` = `dds0` and `dds_plus` = `dds1` on `RamanBeamPair` (post-import patch) | `raman_pulse_test.py` runs without AttributeError | This alias was removed from the class during a refactor; verify the intended mapping (`dds0` = 150 MHz plus-sideband beam, `dds1` = 80 MHz) with whoever last updated `raman_beams.py` |
| DAC-controlled DDS channels (`dac_control_bool = True`) call `SimZotino.write_dac` / `load` which are no-ops | Power-servo setpoints are recorded in the DDS object's `.v_pd` attribute but never written to hardware | PD-voltage-based power control is not validated |

---

## Zotino DAC (`SimZotino`)

| Assumption | Effect | Check |
|---|---|---|
| `write_dac(ch, V)` and `set_dac(voltages)` are logged | DAC voltage states are tracked per-channel | ✓ |
| `write_dac_mu` conversion assumes `vref = 10 V`, bipolar range −10 V to +10 V: `V = (value/0xFFFF)*20 − 10` | Correct for the standard Zotino configuration; wrong if a different reference is used | Verify vref against hardware configuration |
| `load()` is a no-op | The DAC update strobe is not modeled; all `write_dac` calls are treated as immediately effective | Experiments that write multiple channels then call `load()` to apply them simultaneously will see them logged at write time, not at load time |

---

## Urukul CPLD (`SimUrukulCPLD`)

| Assumption | Effect | Check |
|---|---|---|
| `init()`, `set_att()`, `cfg_sw()` are no-ops | CPLD initialisation is assumed instantaneous and always succeeds | Switch-on sequencing and per-channel attenuation are not enforced |

---

## Sampler ADC (`SimSampler`)

| Assumption | Effect | Check |
|---|---|---|
| `sample()` / `sample_mu()` do not fill the buffer | Any code reading from the Sampler buffer after `sample()` will read whatever was in the buffer before (typically zeros from initialisation) | Feedback loops or adaptive routines driven by Sampler readings will use zero as their input |

---

## Shuttler

| Assumption | Effect | Check |
|---|---|---|
| All Shuttler methods (`set_waveform`, `smooth_mu`, `trigger`, `enable`, `init`) are no-ops | Ion-transport waveforms are silently dropped | Shuttler-based transport sequences produce no motion; any experiment that conditions later steps on shuttler completion may still proceed |

---

## AWG / Spectrum Instrumentation (`spcm` stub)

| Assumption | Effect | Check |
|---|---|---|
| `Card`, `Channels`, `Trigger`, `DDSCommandList` are all no-ops | No waveform is written to the AWG | Tweezer trap depth, position, and painting are not simulated |
| `avail_freq_slope_step()` and `avail_amp_slope_step()` return `0.0` | Slope-clipping guard in `TweezerTrap.compute_slopes()` never activates | Computed slopes are used as-is; if they exceed real hardware limits the sim will not warn |
| `units` is a genuine `pint.UnitRegistry` with spcm unit definitions | Unit arithmetic (`50 * units.ohm`, `0.428 * units.V`, etc.) is physically correct | Unit definitions match the real spcm library; only the hardware calls are stubbed |

---

## Cameras — Basler USB (`pypylon` stub)

| Assumption | Effect | Check |
|---|---|---|
| `TlFactory.EnumerateDevices()` returns `[]` | No camera is found; `setup_camera=False` is required for sim runs | Passing `setup_camera=True` will attempt camera initialisation and likely fail |
| `RetrieveResult()` returns `None` | No image data is returned | Any image-analysis step will receive `None` |

---

## Cameras — Andor EMCCD (`pylablib` Andor stub)

| Assumption | Effect | Check |
|---|---|---|
| `read_newest_image()` returns `np.zeros((1,1), dtype=np.uint16)` | Image data is always a 1×1 zero array | Atom-number extraction and absorption imaging will yield zero counts |
| `get_temperature()` returns `20.0` °C | Temperature is always "warm"; no CCD cooling modeled | |
| SDK function calls (`atmcd32d_lib.wlib.*`) are no-ops via `__getattr__` catch-all | All low-level SDK operations silently succeed | |

---

## Oscilloscopes (`vxi11` + `pylablib.Tektronix` stubs)

| Assumption | Effect | Check |
|---|---|---|
| `vxi11.Instrument` is a no-op base class | All scope reads return `None` / empty | `ScopeData` objects will carry no waveform data; `arm_scopes()` in `init_scan_kernel` will do nothing |

---

## Magnetometer (`HMRClient`)

| Assumption | Effect | Check |
|---|---|---|
| `get_field_magnitude()` times out (no server); code retries 5 times then logs and continues | Magnetic field reading is always unavailable; `self.data.b` receives the failure return value | Any experiment logic conditioned on field magnitude will use that value |

---

## Motors — Thorlabs Kinesis / Newport Picomotor

| Assumption | Effect | Check |
|---|---|---|
| `KinesisMotor` and `Picomotor8742` are no-ops | Waveplate and beam-pointing motors do not move | Polarisation control and alignment corrections are silently dropped |

---

## GUI / Qt (`PyQt6` stub)

| Assumption | Effect | Check |
|---|---|---|
| All Qt classes are no-ops | GUI windows do not open; signals are collected but never dispatched | `MonitorController` and live-view widgets instantiate without error but produce no output |

---

## Monitor server (`CommClient` / `MonitorClient`)

| Assumption | Effect | Check |
|---|---|---|
| `send_message()` is a no-op (patched in `sitecustomize.py`) | No TCP connection is attempted to `192.168.1.76:6789`; the lab dashboard receives no signals | The `Generator.generate()` call still runs and updates `device_state_config.json` correctly; only the network signal is suppressed |

---

## `device_state_config.json`

| Assumption | Effect | Check |
|---|---|---|
| All DDS, DAC, TTL device states start empty (`{}`) | `MonitorController` loads without error; no prior hardware state is restored | Experiments that rely on `MonitorController` to restore a previously saved state will start from defaults |

---

## Sim/HAL layer files (not in any lab repo)

| File | What it contains | Arbitrary decisions? |
|---|---|---|
| `sim/stub_devices.py` | Hardware stub classes; all assumptions documented in this file | No — every assumption has a Check column |
| `sitecustomize.py` | Python startup patches; each patch has an explicit documented reason | No |
| `sim/device_db.py` | 224-entry device database mirroring hardware layout | No — channel assignments sourced from `kexp/config/` |
| `sim/device_labels.py` | Name/group/colour mappings for viewer; `default_freq_MHz` sourced from `dds_id.py` with line citations | System groupings and colours are cosmetic choices (viewer-only, no physics) |
| `sim/constraints.py` | Physical operating bounds for DDS validation | **Starts empty. Must only be filled by lab members with hardware knowledge. Nothing is pre-populated by the sim.** |
| `sim/viewer.py` | Web viewer; reads all config from `device_labels.py` and `constraints.py` | No physics assumptions |

### Checksum semantics
`sim/device_labels.checksum_events(events)` is SHA-256 of raw FPGA output events only.
It does **not** depend on `device_labels.py`, `constraints.py`, or any sim configuration.
The hash changes if and only if the hardware output changes (frequencies, amplitudes, voltages, TTL states, or their timestamps).
