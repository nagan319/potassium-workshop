# POTASSIUM-WORKSHOP

ARTIQ simulation environment for cold-K experiments at UCSB.

This is a **meta-workspace** — it contains the simulation HAL and environment definition, but not the lab code itself. The six lab repositories (`artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, `pyLabLib`) are cloned separately on first setup.

---

## Setup

### 1. Install Docker

- **Linux (Fedora/RHEL):** `sudo dnf install docker && sudo systemctl enable --now docker`
- **Linux (Ubuntu/Debian):** follow [docs.docker.com/engine/install/ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- **Mac / Windows:** install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure it is running

### 2. Clone this repo

```bash
git clone https://github.com/nagan319/POTASSIUM-WORKSHOP.git
cd POTASSIUM-WORKSHOP
```

### 3. Pull the image and clone the lab repos

```bash
docker pull ghcr.io/nagan319/potassium-workshop:latest
```

```bash
docker run --rm -v "$(pwd):/workspace" -e GIT_CONFIG_PARAMETERS="'http.sslBackend=openssl' 'http.sslVerify=false'" ghcr.io/nagan319/potassium-workshop:latest bash manage_lab.sh
```

Run the `docker run` line again at any time to pull updates.

> **Linux note:** if you get a permission error on `docker run`, either add yourself to the docker group (`sudo usermod -aG docker $USER`, then log out and back in) or prefix the command with `sudo`.

### 4. Run an experiment

```bash
docker run --rm -it -v "$(pwd):/workspace" ghcr.io/nagan319/potassium-workshop:latest python3 -m artiq.frontend.artiq_run --device-db sim/device_db.py k-exp/kexp/experiments/test/raman_pulse_test.py
```

### 5. View results

```bash
docker run --rm -it -v "$(pwd):/workspace" -p 8765:8765 ghcr.io/nagan319/potassium-workshop:latest python3 sim/viewer.py
```

Open `http://localhost:8765` in your browser.

---

## Viewer

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
├── flake.nix            # Nix flake — builds the Docker image
├── shell.nix            # Nix shell — alternative for systems where Nix is available
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
