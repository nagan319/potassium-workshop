"""Stub for pylablib.devices.Thorlabs — satisfies KinesisMotor import."""


class KinesisMotor:
    """Stub for Thorlabs Kinesis motor controller. All calls are no-ops."""

    def __init__(self, device_id=None, **kwargs):
        self._position = 0
        self._homed = False

    def close(self):
        pass

    def _home(self, force=False):
        self._homed = True

    def _move_to(self, position):
        self._position = position

    def _move_by(self, steps):
        self._position += steps

    def _setup_velocity(self, min_velocity=0, acceleration=0, max_velocity=0):
        pass

    def _is_moving(self):
        return False

    def _get_position(self):
        return self._position

    def _set_position_reference(self):
        pass

    def _is_homed(self):
        return self._homed
