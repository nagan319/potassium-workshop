# POTASSIUM-WORKSHOP

ARTIQ simulation environment for cold-K experiments at UCSB.

This is a **meta-workspace** — it contains the Nix environment and simulation HAL, but not the lab code itself. The six lab repositories (`artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, `pyLabLib`) are cloned separately on first setup.

---

## Setup

### 1. Install Nix

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon
```

### 2. Clone this repo and the lab repos

```bash
git clone https://github.com/ucsb-amo/POTASSIUM-WORKSHOP.git
cd POTASSIUM-WORKSHOP
./manage_lab.sh
```

`manage_lab.sh` clones `artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, and `pyLabLib` from `https://github.com/ucsb-amo/`. Run it again at any time to pull updates.

### 3. Enter the environment

```bash
nix-shell
```

This drops you into a shell with Python 3.10, all physics packages (ARC, lmfit, pint, …), and the correct `PYTHONPATH` pointing at the lab repos.

---

## Running an Experiment

```bash
# inside nix-shell
artiq-run --device-db sim/device_db.py \
  k-exp/kexp/experiments/test/raman_pulse_test.py
```

Each run saves a JSON Lines event log to `sim-data/logs/run_NNNNNN_<filename>.jsonl`.

---

## Viewing Results

```bash
# inside nix-shell
python3 sim/viewer.py
```

Open `http://localhost:8765` in your browser. The viewer shows:

- **TTL** — digital output states vs time, grouped by system (Raman, Imaging, Cooling, …)
- **DDS** — frequency, amplitude, and attenuation vs time per channel
- **DAC** — Zotino voltage outputs vs time
- **SHA-256 checksum** — fingerprint of raw FPGA output events (click to copy)
- **Constraint warnings** — out-of-range events if `sim/constraints.py` has entries

---

## Adding Physical Constraints

`sim/constraints.py` is intentionally empty. **Only lab members with direct hardware knowledge should add entries.** Each constraint requires a citation:

```python
DDS_CONSTRAINTS = {
    "urukul4_ch2": {
        "valid_range_MHz": (60, 120),
        "set_by": "JE",
        "source": "80 MHz AOM datasheet bandwidth spec, verified 2026-03-22",
    },
}
```

Constraints appear as warnings in the viewer and do **not** affect the SHA-256 checksum.

---

## Repository Layout

```
POTASSIUM-WORKSHOP/
├── shell.nix            # Nix shell — reproducible Python environment
├── flake.nix            # Nix flake (alternative entry point, also builds Docker image)
├── manage_lab.sh        # Clone/update the 6 lab repos from ucsb-amo/
├── sitecustomize.py     # Python startup patches (ARTIQ sim, autosave, MonitorClient stub)
├── SIM_ASSUMPTIONS.md   # Every assumption made by the simulation HAL
└── sim/
    ├── device_db.py     # 224-entry ARTIQ device database (mirrors hardware layout)
    ├── stub_devices.py  # Hardware stub classes (SimCore, SimAD9910, SimZotino, …)
    ├── device_labels.py # TTL/DDS display names and system groupings for the viewer
    ├── constraints.py   # Physical operating bounds (empty by default, expert-set only)
    └── viewer.py        # Web-based FPGA output viewer (Plotly.js, stdlib HTTP)
```

Lab repos (not in this repo, cloned by `manage_lab.sh`):

```
artiq/   k-exp/   wax/   k-amo/   spcm/   pyLabLib/
```

---

## Simulation Architecture

`sitecustomize.py` runs before any Python import and patches:

- `artiq.language.core.delay` → converts seconds to integer nanoseconds, advances the machine-unit clock
- `artiq.language.environment.HasEnvironment` → injects `sim-data/` as the dataset backend
- `waxx.base.expt.Expt.end_wax` → saves a JSONL hardware event log at experiment end
- `kexp.clients.monitor.CommClient.send_message` → suppresses TCP calls to the lab dashboard

All assumptions are documented in `SIM_ASSUMPTIONS.md`.
