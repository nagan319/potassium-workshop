"""Stub for pylablib.devices.Andor.atmcd32d_lib."""


class _WLib:
    """No-op proxy for all SDK function calls."""
    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None
        return _noop


wlib = _WLib()
