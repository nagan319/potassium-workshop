# POTASSIUM-WORKSHOP

ARTIQ simulation environment for cold-K experiments at UCSB.

This repo is a **meta-workspace** — it contains the Nix/Docker environment and
simulation HAL, but not the lab code itself. The six lab repositories
(`artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, `pyLabLib`) are cloned separately
and mounted at runtime.

---

## Prerequisites

Install one of the following on your machine:

| Option | Requirement |
|---|---|
| Nix shell (recommended for dev) | [Nix](https://nixos.org/download) with flakes enabled |
| Docker | Docker Desktop or Docker Engine |
| Apptainer | Apptainer ≥ 1.1 (HPC clusters, no root required) |

---

## Quick Start (any option)

### Step 1 — Clone this repo

```bash
git clone https://github.com/ucsb-amo/POTASSIUM-WORKSHOP.git
cd POTASSIUM-WORKSHOP
```

### Step 2 — Clone the lab repos

```bash
./manage_lab.sh
```

This clones `artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, and `pyLabLib` from
`https://github.com/ucsb-amo/` into the workspace directory.  Run it again at
any time to pull updates.

### Step 3 — Enter the environment (choose one)

---

#### Option A: Nix shell (flakes)

```bash
nix develop
```

Requires Nix with flakes.  To enable flakes permanently:

```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

#### Option A (classic): Nix shell without flakes

```bash
nix-shell
```

Uses `shell.nix` — no flake configuration needed.

---

#### Option B: Docker

Build the image once (takes a few minutes, downloads the Nix store):

```bash
nix build .#dockerImage && docker load < result
```

Then run experiments by mounting your workspace:

```bash
docker run --rm -it \
  -v "$(pwd):/workspace" \
  potassium-workshop:latest \
  python3 k-exp/kexp/experiments/test/raman_pulse_test.py \
    --device-db sim/device_db.py
```

To open an interactive shell inside the container:

```bash
docker run --rm -it -v "$(pwd):/workspace" potassium-workshop:latest bash
```

#### Option B (pre-built): Pull from GitHub Container Registry

```bash
docker pull ghcr.io/ucsb-amo/potassium-workshop:latest
docker run --rm -it \
  -v "$(pwd):/workspace" \
  ghcr.io/ucsb-amo/potassium-workshop:latest \
  python3 k-exp/kexp/experiments/test/raman_pulse_test.py \
    --device-db sim/device_db.py
```

---

#### Option C: Apptainer (no root, HPC clusters)

```bash
apptainer pull docker://ghcr.io/ucsb-amo/potassium-workshop:latest

apptainer run \
  --bind "$(pwd):/workspace" \
  potassium-workshop_latest.sif \
  python3 k-exp/kexp/experiments/test/raman_pulse_test.py \
    --device-db sim/device_db.py
```

---

## Running an Experiment

Inside any environment (nix shell, Docker, or Apptainer):

```bash
python3 k-exp/kexp/experiments/test/raman_pulse_test.py \
  --device-db sim/device_db.py
```

Or use the `artiq-run` alias (Nix shell only):

```bash
artiq-run --device-db sim/device_db.py \
  k-exp/kexp/experiments/test/raman_pulse_test.py
```

Each run saves a JSON Lines log to `sim-data/logs/run_NNNNNN_<filename>.jsonl`.

---

## Viewing Results

Start the web viewer (inside any environment):

```bash
python3 sim/viewer.py
```

Then open `http://localhost:8765` in your browser.

The viewer shows:
- **TTL** — digital output states vs time, grouped by system (Raman, Imaging, etc.)
- **DDS** — frequency, amplitude, and attenuation vs time per channel
- **DAC** — Zotino voltage outputs vs time
- **SHA-256 checksum** — fingerprint of raw FPGA output events (click to copy)
- **Constraint warnings** — if `sim/constraints.py` has entries, out-of-range events are flagged

---

## Adding Physical Constraints

`sim/constraints.py` is intentionally empty.  **Only lab members with direct
hardware knowledge should add entries.**  Each constraint requires a citation
(datasheet spec, calibration date, or experimental measurement):

```python
DDS_CONSTRAINTS = {
    "urukul4_ch2": {
        "valid_range_MHz": (60, 120),
        "set_by": "JE",
        "source": "80 MHz AOM datasheet bandwidth spec, verified 2026-03-22",
    },
}
```

Constraints affect only the warning panel in the viewer.  They do **not**
change the SHA-256 checksum.

---

## Pushing a Docker Image to GHCR

```bash
# Build
nix build .#dockerImage

# Copy to GitHub Container Registry
skopeo copy \
  nix:$(nix build .#dockerImage --print-out-paths --no-link) \
  docker://ghcr.io/ucsb-amo/potassium-workshop:latest
```

`skopeo` must be authenticated: `skopeo login ghcr.io -u <github-username>`.

---

## Repository Layout

```
POTASSIUM-WORKSHOP/
├── flake.nix            # Nix flake — Python env + Docker image definition
├── shell.nix            # Classic Nix shell (no flakes required)
├── manage_lab.sh        # Clone/update the 6 lab repos from ucsb-amo/
├── sitecustomize.py     # Python startup patches (ARTIQ sim, MonitorClient stub)
├── SIM_ASSUMPTIONS.md   # Every assumption made by the simulation HAL
├── sim/
│   ├── device_db.py     # 224-entry ARTIQ device database (mirrors hardware)
│   ├── stub_devices.py  # Hardware stub classes (SimCore, SimAD9910, …)
│   ├── device_labels.py # TTL/DDS display names and system groupings for viewer
│   ├── constraints.py   # Physical operating bounds (fill in with hardware knowledge)
│   └── viewer.py        # Web-based FPGA output viewer (Plotly.js, stdlib HTTP)
└── sim-data/            # Generated at runtime — logs/, run_id.py, device_state_config.json
```

Lab repos (not in this repo, cloned by `manage_lab.sh`):

```
artiq/     k-exp/     wax/     k-amo/     spcm/     pyLabLib/
```

---

## Simulation Architecture

`sitecustomize.py` loads before any Python import and applies patches:

- `artiq.language.core.delay` → converts seconds to integer nanoseconds before
  advancing the machine-unit clock (`SimCore.now_mu`)
- `artiq.language.environment.HasEnvironment` → injects `sim-data/` dataset backend
- `waxx.base.expt.Expt.end_wax` → saves a JSONL event log at experiment end
- `kexp.clients.monitor.CommClient.send_message` → suppresses TCP calls to lab dashboard

All simulation assumptions are documented in `SIM_ASSUMPTIONS.md`.
