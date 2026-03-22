# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Overview

This is a multi-repository workspace for quantum physics experiments with cold Potassium atoms at UCSB. It contains 6 separate git repositories:

- **k-exp** — Main experiment code for the K machine (ARTIQ-based control)
- **artiq** — Real-time quantum control framework (external, from UCSB-AMO fork)
- **k-amo** — AMO physics utilities (polarizabilities, force calculations)
- **wax** — Waveform generation and experiment data framework (two sub-packages: `waxa`, `waxx`)
- **spcm** — Python interface for Spectrum Instrumentation DAC/ADC cards
- **pyLabLib** — Generic device control library (cameras, stages, oscilloscopes)

Each subdirectory is its own git repo. The `manage_lab.sh` script syncs all repos from `https://github.com/ucsb-amo/`.

## Common Commands

```bash
# Sync all repositories from GitHub
./manage_lab.sh

# Install a package in development mode (run inside the repo)
pip install -e .

# Install spcm with optional CUDA support
cd spcm && pip install -e ".[cuda]"
```

## k-exp Architecture

The primary working repository. All experiments inherit from `Base` via ARTIQ's `EnvExperiment`.

**Inheritance chain for experiments:**
```
artiq.EnvExperiment
  └── waxx.Expt
        └── kexp.base.Base  (also inherits: Devices, Cooling, Image, Cameras, Control, Clients)
              └── Individual experiment classes
```

**Key modules in `kexp/`:**
- `base/` — Mix-in base classes: `Devices` (hardware init), `Cooling` (MOT/GM/evap sequences), `Image` (camera/imaging control), `Cameras`, `Control`, `Clients`
- `config/` — Hardware identity maps: `dds_id.py`, `ttl_id.py`, `dac_id.py`, `camera_id.py`, `sampler_id.py`, `shuttler_id.py`; experiment parameters in `expt_params.py`; network paths in `ip.py`
- `control/` — Device controllers: coils, lasers, AWGs, ethernet relays, SLM, tweezers
- `experiments/` — Experiment scripts organized by person (JE/, JK/, JP/, HF_experiments/) and type (calibrations/, test/)
- `calibrations/` — Calibration routines for imaging, magnets, tweezers
- `util/` — GUIs, live data visualization, ARTIQ async print, remote control helpers

**Experiment parameter access:** `self.p` (alias for `self.params`, an `ExptParams` instance). Physical timing constants (e.g., `self.p.t_imaging_pulse`) and all scan variables live here.

**Data flow:** `waxa.DataSaver` handles HDF5 file saving; `kexp.config.data_vault.DataVault` wraps experiment-level data storage. Network paths and server communication are configured in `kexp/config/ip.py`.

**ARTIQ kernel methods** are decorated with `@kernel`. The `init_kernel()` method resets hardware and initializes all subsystems. `finish_prepare()` must be called at the end of `prepare()` in experiments.

## wax Architecture

Two sub-packages installed separately:
- **waxa** (`wax/waxa-src/`) — Data saving (`waxa.data.DataSaver`), HDF5-based
- **waxx** (`wax/waxx-src/`) — Experiment base class (`waxx.Expt`), image type constants, timing configuration, parameter base class (`waxx.config.expt_params.ExptParams`)

`kexp.config.expt_params.ExptParams` extends `waxx.config.expt_params.ExptParams`.

## ARTIQ Context

ARTIQ uses a host/core-device split. Code decorated with `@kernel` compiles to RTIO (real-time I/O) and runs on the FPGA core device with nanosecond timing. Host Python runs on the control PC and communicates via RPC. Key constraint: kernel code cannot use arbitrary Python — only a restricted subset that the ARTIQ compiler supports.

Launch tools: `artiq_master`, `artiq_dashboard`, `artiq_client`, `artiq_run`, `artiq_compile`.
