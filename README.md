# POTASSIUM-WORKSHOP

ARTIQ simulation environment for cold-K experiments at UCSB.

This is a **meta-workspace** — it contains the simulation HAL and environment definition, but not the lab code itself. The six lab repositories (`artiq`, `k-exp`, `wax`, `k-amo`, `spcm`, `pyLabLib`) are cloned separately on first setup.

---

## Setup

### 1. Install Docker

- **Linux (Fedora/RHEL):** `sudo dnf install docker && sudo systemctl enable --now docker`
- **Linux (Ubuntu/Debian):** follow [docs.docker.com/engine/install/ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- **Mac / Windows:** install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure it is running

> **Linux note:** if you get a permission error on `docker` commands, add yourself to the docker group (`sudo usermod -aG docker $USER`) and log out and back in.

### 2. Clone this repo

```bash
git clone https://github.com/nagan319/POTASSIUM-WORKSHOP.git
cd POTASSIUM-WORKSHOP
```

### 3. Pull the image and clone the lab repos

```bash
./run pull
./run lab
```

Run `./run lab` again at any time to pull updates from the lab repos.

---

## Running Experiments

```bash
./run experiment k-exp/kexp/experiments/test/raman_pulse_test.py
```

Each run saves a JSON Lines event log to `sim-data/logs/run_NNNNNN_<filename>.jsonl`.

## Viewing Results

```bash
./run viewer
```

Open `http://localhost:8765`. The viewer shows TTL/DDS/DAC outputs vs time, a SHA-256 checksum of the FPGA event log, and any constraint warnings.

## Interactive Shell

```bash
./run shell
```

Opens a bash shell inside the container with the full Python environment and PYTHONPATH set up.

---

## Development

This project uses [Claude Code](https://claude.ai/code) as its AI development assistant. `CLAUDE.md` and `SIM_ASSUMPTIONS.md` provide the context Claude needs to work effectively in this codebase.

To start a development session after cloning:

```bash
# Install Claude Code (one-time)
npm install -g @anthropic-ai/claude-code

# Start Claude in the workspace
claude
```

Claude has access to all workspace files and can run `docker exec` commands into a running container. For interactive debugging, start a named container first:

```bash
docker run -d --name potassium --rm -it -v "$(pwd):/workspace" ghcr.io/nagan319/potassium-workshop:latest bash
# ... work with Claude ...
docker stop potassium
```

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
├── run                  # Shorthand script for common Docker operations
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

Lab repos (not in this repo, cloned by `./run lab`):

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
