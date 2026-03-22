"""Stub for PyQt6.QtCore — no-op stand-ins for all names used across waxx/k-exp."""


# ── Signal / slot infrastructure ────────────────────────────────────────────

class _Signal:
    def connect(self, *args, **kwargs): pass
    def disconnect(self, *args, **kwargs): pass
    def emit(self, *args, **kwargs): pass


class _SignalDescriptor:
    """Class-body descriptor returned by pyqtSignal(). Returns a _Signal on access."""
    def __get__(self, obj, objtype=None):
        return _Signal()
    def connect(self, *args, **kwargs): pass
    def disconnect(self, *args, **kwargs): pass
    def emit(self, *args, **kwargs): pass


def pyqtSignal(*args, **kwargs):
    return _SignalDescriptor()


def pyqtSlot(*args, **kwargs):
    """Decorator — pass-through."""
    def decorator(func):
        return func
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return args[0]
    return decorator


# ── QObject ──────────────────────────────────────────────────────────────────

class QObject:
    def __init__(self, parent=None): pass
    def moveToThread(self, thread): pass
    def deleteLater(self): pass
    def thread(self): return None
    def connect(self, *a, **kw): pass


# ── QThread ──────────────────────────────────────────────────────────────────

class QThread(QObject):
    started = _SignalDescriptor()
    finished = _SignalDescriptor()

    def __init__(self, parent=None): pass
    def start(self, priority=None): pass
    def quit(self): pass
    def wait(self, deadline=None): return True
    def run(self): pass
    def isRunning(self): return False
    def isFinished(self): return True
    def terminate(self): pass
    def requestInterruption(self): pass
    def isInterruptionRequested(self): return False
    def setPriority(self, priority): pass

    @staticmethod
    def currentThread(): return QThread()
    @staticmethod
    def sleep(secs): pass
    @staticmethod
    def msleep(msecs): pass
    @staticmethod
    def usleep(usecs): pass


# ── QTimer ───────────────────────────────────────────────────────────────────

class QTimer(QObject):
    timeout = _SignalDescriptor()

    def __init__(self, parent=None): pass
    def start(self, interval=None): pass
    def stop(self): pass
    def setInterval(self, msec): pass
    def interval(self): return 0
    def setSingleShot(self, singleShot): pass
    def isSingleShot(self): return False
    def isActive(self): return False

    @staticmethod
    def singleShot(interval, callback): pass


# ── QSignalBlocker ────────────────────────────────────────────────────────────

class QSignalBlocker:
    def __init__(self, obj): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def reblock(self): pass
    def unblock(self): pass


# ── Geometry helpers ─────────────────────────────────────────────────────────

class QSize:
    def __init__(self, w=0, h=0):
        self.width = w
        self.height = h
    def __repr__(self): return f"QSize({self.width}, {self.height})"


class QPoint:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class QRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x; self.y = y; self.width = w; self.height = h
    def left(self): return self.x
    def top(self): return self.y
    def right(self): return self.x + self.width
    def bottom(self): return self.y + self.height


class QMargins:
    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left; self.top = top; self.right = right; self.bottom = bottom


# ── Qt namespace ─────────────────────────────────────────────────────────────

class Qt:
    # Alignment
    AlignLeft        = 0x0001
    AlignRight       = 0x0002
    AlignHCenter     = 0x0004
    AlignTop         = 0x0020
    AlignBottom      = 0x0040
    AlignVCenter     = 0x0080
    AlignCenter      = AlignHCenter | AlignVCenter

    # Window flags
    Window           = 0x00000001
    Dialog           = 0x00000002
    FramelessWindowHint = 0x00000800
    WindowStaysOnTopHint = 0x00040000

    # Orientation
    Horizontal       = 0x1
    Vertical         = 0x2

    # Focus policy
    NoFocus          = 0
    StrongFocus      = 11

    # Check state
    Unchecked        = 0
    PartiallyChecked = 1
    Checked          = 2

    # Scroll bar policy
    ScrollBarAlwaysOff  = 1
    ScrollBarAlwaysOn   = 2
    ScrollBarAsNeeded   = 0

    # Sort order
    AscendingOrder  = 0
    DescendingOrder = 1

    # Text interaction
    NoTextInteraction           = 0
    TextSelectableByMouse       = 1
    TextSelectableByKeyboard    = 2
    LinksAccessibleByMouse      = 4
    LinksAccessibleByKeyboard   = 8
    TextEditable                = 16
    TextEditorInteraction       = TextSelectableByMouse | TextSelectableByKeyboard | TextEditable

    # Pen/brush
    NoPen    = 0
    SolidLine = 1
    NoBrush  = 0
    SolidPattern = 1

    # Cursor
    ArrowCursor     = 0
    WaitCursor      = 3
    CrossCursor     = 10
    PointingHandCursor = 13

    # Key modifiers
    NoModifier      = 0x00000000
    ShiftModifier   = 0x02000000
    ControlModifier = 0x04000000
    AltModifier     = 0x08000000

    # Widget attributes
    WA_TranslucentBackground = 120
    WA_NoSystemBackground    = 9

    # Size policy
    class SizePolicy:
        Fixed            = 0
        Minimum          = 1
        Maximum          = 4
        Preferred        = 5
        Expanding        = 7
        MinimumExpanding = 3
        Ignored          = 13

    # Misc
    ElideRight  = 0x0001
    ElideLeft   = 0x0002
    ElideMiddle = 0x0004
    ElideNone   = 0x0000

    DisplayRole = 0
    EditRole    = 1
    UserRole    = 256

    class GlobalColor:
        white  = 3
        black  = 2
        red    = 7
        green  = 8
        blue   = 9
        yellow = 11
        cyan   = 10
        magenta = 12
        gray   = 5
        darkGray = 4
        transparent = 19

    white  = 3
    black  = 2
    red    = 7
    green  = 8
    blue   = 9
    yellow = 11
    cyan   = 10
    magenta = 12
    gray   = 5
    darkGray = 4
    transparent = 19
