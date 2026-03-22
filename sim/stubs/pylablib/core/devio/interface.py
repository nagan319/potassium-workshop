"""Stub for pylablib.core.devio.interface."""


def use_parameters(*args, **kwargs):
    """Stub decorator factory. Returns a pass-through decorator."""
    # Handle both @use_parameters and @use_parameters(...) forms
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return args[0]

    def decorator(func):
        return func

    return decorator
