"""Stub for pypylon.pylon — satisfies BaslerUSB class definition without Basler SDK."""


class DeviceInfo:
    def GetSerialNumber(self):
        return ""


class TlFactory:
    @staticmethod
    def GetInstance():
        return _tl_factory_instance

    def EnumerateDevices(self):
        return []

    def CreateFirstDevice(self, info=None):
        return None

    def CreateDevice(self, info):
        return None


_tl_factory_instance = TlFactory()


class InstantCamera:
    """Stub base class for BaslerUSB."""

    def __init__(self, device=None):
        pass

    def Open(self):
        pass

    def Close(self):
        pass

    def IsOpen(self):
        return False

    def StartGrabbing(self, *args, **kwargs):
        pass

    def StopGrabbing(self):
        pass

    def IsGrabbing(self):
        return False

    def RetrieveResult(self, timeout, *args, **kwargs):
        return None

    def GetNodeMap(self):
        return _NodeMap()


class _NodeMap:
    def GetNode(self, name):
        return _Node()


class _Node:
    def SetValue(self, value):
        pass

    def GetValue(self):
        return None


GrabStrategy_LatestImageOnly = 0
GrabStrategy_OneByOne = 1
TimeoutHandling_ThrowException = 0
TimeoutHandling_Return = 1
