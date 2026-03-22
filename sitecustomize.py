"""sitecustomize.py — loaded automatically by Python's site module at startup.

Patches artiq.language.core.kernel so that @kernel-decorated methods on objects
that lack a 'core' attribute (e.g. waxx DDS/TTL wrapper classes) fall back to
direct Python execution instead of raising AttributeError.

Why this is needed
------------------
In real ARTIQ, nested @kernel calls (a kernel calling another kernel) are
compiled into a single FPGA binary; the runtime never does getattr(self, "core")
for the inner call.  In simulation mode every @kernel dispatch goes through
  getattr(self, core_name).run(...)
at runtime.  Wrapper classes like waxx.control.artiq.DDS.DDS have @kernel
methods but no self.core — they rely on the ARTIQ compiler to handle dispatch.
The patch below adds a graceful fallback: if self.core is absent, execute the
function body directly as plain Python.  For simulation all hardware calls are
already no-ops in stub_devices.py, so this is safe.

This patch must run before any artiq module is imported (sitecustomize.py loads
at interpreter startup, before user code), so the @kernel decorator applied to
DDS, TTL, etc. at class-definition time picks up the patched version.
"""

import artiq.language.core as _core
from functools import wraps


def _sim_kernel(arg=None, flags={}):
    """@kernel replacement: falls back to plain Python when self.core is absent."""
    if isinstance(arg, str):
        core_name = arg

        def inner_decorator(function):
            @wraps(function)
            def run_on_core(self, *k_args, **k_kwargs):
                core = getattr(self, core_name, None)
                if core is None:
                    # No core device on this object — run directly as Python.
                    return function(self, *k_args, **k_kwargs)
                return core.run(run_on_core, ((self,) + k_args), k_kwargs)

            run_on_core.artiq_embedded = _core._ARTIQEmbeddedInfo(
                core_name=core_name,
                portable=False,
                function=function,
                syscall=None,
                forbidden=False,
                destination=None,
                flags=set(flags),
            )
            return run_on_core

        return inner_decorator

    elif arg is None:
        return lambda f: _sim_kernel(f, flags)
    else:
        # Plain @kernel with no arguments — default core name is "core"
        return _sim_kernel("core", flags)(arg)


_core.kernel = _sim_kernel

# ── delay() unit fix ──────────────────────────────────────────────────────────
# artiq.language.core.delay(dt_seconds) calls _time_manager.take_time(dt),
# while delay_mu(n) calls take_time_mu(n).  artiq.sim.time.Manager maps
# take_time = take_time_mu, so both feed the *same* counter.
#
# With SimCore.ref_period = 1e-9 (hardware-accurate: 1 MU = 1 ns), a
# delay(1e-3) should advance the cursor by 1_000_000 MU, but without this
# patch it only advances by 0.001 "sim units" — three orders of magnitude wrong.
#
# Patch: replace delay() so it converts seconds → integer nanoseconds before
# calling take_time_mu, making it consistent with delay_mu().
_SIM_REF_PERIOD = 1e-9   # seconds per machine unit (1 ns)

def _sim_delay(dt):
    """delay() replacement that feeds nanoseconds into the MU counter."""
    _core._time_manager.take_time_mu(int(round(dt / _SIM_REF_PERIOD)))

_core.delay = _sim_delay


# ── Post-import patches for sim compatibility ─────────────────────────────
# These hook into the import system to patch classes after their modules load,
# without touching any lab repo file.

import sys as _sys


class _PostImportPatcher:
    """sys.meta_path hook that patches specific modules after first import.

    Works by intercepting find_module, then deferring to the real importer but
    adding attributes after the module is fully loaded.
    """

    _patches = {}  # module_name -> list of (callable(mod) -> None)

    def find_module(self, name, path=None):
        return self if name in self._patches else None

    def load_module(self, name):
        # Remove ourselves first to avoid infinite recursion when the real
        # importer is called below.
        _sys.meta_path.remove(self)
        try:
            import importlib
            mod = importlib.import_module(name)
            for fn in self._patches.get(name, []):
                try:
                    fn(mod)
                except Exception as e:
                    import warnings
                    warnings.warn(f"[sim] post-import patch for {name} failed: {e}")
            return mod
        finally:
            # Re-insert so future imports of other patched modules are caught.
            _sys.meta_path.insert(0, self)

    @classmethod
    def register(cls, module_name, patch_fn):
        cls._patches.setdefault(module_name, []).append(patch_fn)


_patcher = _PostImportPatcher()
_sys.meta_path.insert(0, _patcher)


def _patch_raman_beams(mod):
    """Add dds_minus/dds_plus aliases (= dds0/dds1) to RamanBeamPair.

    raman_pulse_test.py and some _old experiments use these names.  The waxx
    class was refactored to dds0/dds1 but the aliases were never added back.
    """
    cls = mod.RamanBeamPair
    if not hasattr(cls, 'dds_minus'):
        cls.dds_minus = property(lambda self: self.dds0)
    if not hasattr(cls, 'dds_plus'):
        cls.dds_plus = property(lambda self: self.dds1)


_PostImportPatcher.register('waxx.control.raman_beams', _patch_raman_beams)


def _patch_comm_client(mod):
    """No-op all socket sends — lab monitor server is not present in sim.

    CommClient.send_message already has a try/except, but on Linux sock.connect()
    to a non-existent LAN host blocks for several seconds waiting for ARP/TCP
    timeout before raising.  Replacing send_message with a no-op avoids the hang.
    """
    def _noop(self, *args, **kwargs):
        pass
    mod.CommClient.send_message = _noop
    mod.CommClient.close = _noop


_PostImportPatcher.register('waxx.util.comms_server.comm_client', _patch_comm_client)


def _patch_expt_end(mod):
    """Auto-save the sim log at experiment end.

    Wraps Expt.end_wax() so that every experiment run automatically writes
    sim-data/logs/run_NNNNNN.jsonl before the process exits.  The run_id is
    read from sim-data/run_id.py (written/incremented by artiq_run).
    """
    import os
    import pathlib
    original_end = mod.Expt.end_wax

    def _end_with_log(self, *args, **kwargs):
        result = original_end(self, *args, **kwargs)
        try:
            from sim.stub_devices import save_sim_log, _sim_log
            if not _sim_log:
                return result
            workspace = os.environ.get("code", os.getcwd())
            logs_dir = pathlib.Path(workspace) / "sim-data" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            # Determine run_id from waxx run_info, artiq rid, or file fallback.
            rid = None
            try:
                rid = self.run_info.run_id
            except AttributeError:
                pass
            if rid is None:
                rid = getattr(self, "rid", None)
            if rid is None:
                rid_file = pathlib.Path(workspace) / "sim-data" / "run_id.py"
                try:
                    rid = int(rid_file.read_text().strip())
                except Exception:
                    rid = 0
            # Use the source filename stem (e.g. "raman_pulse_test"), not the
            # class name (e.g. "rabi_surf"), because the file name is what the
            # user typed and is more meaningful in the log directory.
            import inspect
            try:
                expt_name = pathlib.Path(inspect.getfile(type(self))).stem
            except (TypeError, OSError):
                expt_name = type(self).__name__
            log_path = logs_dir / f"run_{rid:06d}_{expt_name}.jsonl"
            save_sim_log(str(log_path))
            print(f"[sim] Log saved → {log_path}  ({len(_sim_log)} events)")
        except Exception as e:
            import warnings
            warnings.warn(f"[sim] auto-save log failed: {e}")
        return result

    mod.Expt.end_wax = _end_with_log


_PostImportPatcher.register('waxx.base.expt', _patch_expt_end)
