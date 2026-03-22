"""Stub for pylablib.devices.Newport — satisfies Picomotor8742 import."""


class Picomotor8742:
    """Stub for Newport Picomotor 8742 controller. All calls are no-ops."""

    def __init__(self, host=None, multiaddr=False, scan=False, **kwargs):
        self._position = {}

    def close(self):
        pass

    def move_to(self, axis, position):
        self._position[axis] = position

    def move_by(self, axis, steps):
        self._position[axis] = self._position.get(axis, 0) + steps

    def get_position(self, axis):
        return self._position.get(axis, 0)

    def stop(self, axis=None):
        pass

    def wait_move(self, axis=None, timeout=None):
        pass

    def is_moving(self, axis=None):
        return False

    def home(self, axis, direction=1):
        pass
