"""Stub for pylablib.devices.Andor — satisfies AndorEMCCD class definition."""


class AndorSDK2Camera:
    """Stub base class for AndorEMCCD. All methods are no-ops."""

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def open(self):
        pass

    def set_EM_gain_mode(self, mode):
        pass

    def set_EMCCD_gain(self, gain=0, advanced=False):
        pass

    def set_exposure(self, exposure):
        pass

    def set_trigger_mode(self, mode):
        pass

    def setup_shutter(self, mode="open"):
        pass

    def set_vsspeed(self, speed):
        pass

    def set_vsamplitude(self, amp):
        pass

    def set_hsspeed(self, typ=0, hs_speed=0):
        pass

    def set_acquisition_mode(self, mode):
        pass

    def set_read_mode(self, mode):
        pass

    def set_cooler_mode(self, mode=0):
        pass

    def set_amp_mode(self, preamp=0):
        pass

    def activate_cameralink(self, on=1):
        pass

    def start_acquisition(self):
        pass

    def stop_acquisition(self):
        pass

    def wait_for_frame(self, timeout=None):
        pass

    def read_newest_image(self):
        import numpy as np
        return np.zeros((1, 1), dtype=np.uint16)

    def read_multiple_images(self, *args, **kwargs):
        return []

    def _initial_setup_temperature_fixed(self):
        pass

    def get_temperature(self):
        return 20.0

    def set_temperature(self, temperature):
        pass
