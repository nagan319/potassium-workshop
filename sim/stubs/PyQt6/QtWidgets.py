"""Stub for PyQt6.QtWidgets — no-op stand-ins for all names used across waxx/k-exp."""

from PyQt6.QtCore import _SignalDescriptor, pyqtSignal, QSize


class _Widget:
    """Base no-op widget. All geometry/style/event methods are no-ops."""
    def __init__(self, *args, **kwargs): pass
    def show(self): pass
    def hide(self): pass
    def close(self): pass
    def setVisible(self, v): pass
    def isVisible(self): return False
    def setEnabled(self, e): pass
    def isEnabled(self): return True
    def setFixedSize(self, *args): pass
    def setMinimumSize(self, *args): pass
    def setMaximumSize(self, *args): pass
    def resize(self, *args): pass
    def move(self, *args): pass
    def setWindowTitle(self, t): pass
    def windowTitle(self): return ""
    def setWindowIcon(self, icon): pass
    def setStyleSheet(self, css): pass
    def setFont(self, font): pass
    def setToolTip(self, tip): pass
    def setObjectName(self, name): pass
    def objectName(self): return ""
    def setLayout(self, layout): pass
    def layout(self): return None
    def parentWidget(self): return None
    def update(self): pass
    def repaint(self): pass
    def adjustSize(self): pass
    def sizeHint(self): return QSize(100, 30)
    def minimumSizeHint(self): return QSize(0, 0)
    def setContentsMargins(self, *args): pass
    def setAttribute(self, attr, on=True): pass
    def setFocus(self): pass
    def clearFocus(self): pass
    def hasFocus(self): return False
    def setCursor(self, cursor): pass
    def geometry(self):
        from PyQt6.QtCore import QRect
        return QRect()
    def width(self): return 0
    def height(self): return 0
    def palette(self):
        from PyQt6.QtGui import QPalette
        return QPalette()
    def setPalette(self, palette): pass
    def setAutoFillBackground(self, b): pass


class QWidget(_Widget): pass
class QMainWindow(_Widget):
    def setCentralWidget(self, w): pass
    def centralWidget(self): return None
    def menuBar(self): return _MenuBar()
    def statusBar(self): return _StatusBar()
    def addToolBar(self, *args): return _Widget()


class _MenuBar(_Widget):
    def addMenu(self, *args): return _Widget()
    def addAction(self, *args): return _Widget()


class _StatusBar(_Widget):
    def showMessage(self, msg, timeout=0): pass


class QApplication(_Widget):
    def __init__(self, argv=None): pass
    @staticmethod
    def instance(): return None
    @staticmethod
    def exec(): return 0
    @staticmethod
    def quit(): pass
    @staticmethod
    def setStyle(style): pass
    @staticmethod
    def setApplicationName(name): pass
    @staticmethod
    def processEvents(): pass
    @staticmethod
    def screens(): return []
    @staticmethod
    def primaryScreen():
        from PyQt6.QtGui import QScreen
        return QScreen()


# ── Layout classes ────────────────────────────────────────────────────────────

class _Layout:
    def __init__(self, *args, **kwargs): pass
    def addWidget(self, *args, **kwargs): pass
    def addLayout(self, *args, **kwargs): pass
    def addStretch(self, *args): pass
    def addSpacing(self, n): pass
    def setSpacing(self, n): pass
    def setContentsMargins(self, *args): pass
    def setAlignment(self, *args): pass
    def count(self): return 0
    def itemAt(self, i): return None
    def removeWidget(self, w): pass
    def insertWidget(self, idx, w, *args): pass

class QVBoxLayout(_Layout): pass
class QHBoxLayout(_Layout): pass
class QGridLayout(_Layout):
    def addWidget(self, w, row=0, col=0, rowspan=1, colspan=1, *args, **kwargs): pass


# ── Basic controls ────────────────────────────────────────────────────────────

class QLabel(_Widget):
    def __init__(self, *args, **kwargs): pass
    def setText(self, t): pass
    def text(self): return ""
    def setAlignment(self, a): pass
    def setPixmap(self, p): pass
    def setWordWrap(self, w): pass


class QPushButton(_Widget):
    clicked = _SignalDescriptor()
    toggled = _SignalDescriptor()
    pressed = _SignalDescriptor()
    released = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setText(self, t): pass
    def text(self): return ""
    def setCheckable(self, c): pass
    def isChecked(self): return False
    def setChecked(self, c): pass
    def setIcon(self, icon): pass
    def setIconSize(self, size): pass
    def click(self): pass


class QCheckBox(_Widget):
    stateChanged = _SignalDescriptor()
    toggled = _SignalDescriptor()
    clicked = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setText(self, t): pass
    def text(self): return ""
    def isChecked(self): return False
    def setChecked(self, c): pass
    def setTristate(self, t): pass
    def checkState(self): return 0


class QLineEdit(_Widget):
    textChanged = _SignalDescriptor()
    textEdited = _SignalDescriptor()
    returnPressed = _SignalDescriptor()
    editingFinished = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setText(self, t): pass
    def text(self): return ""
    def setPlaceholderText(self, t): pass
    def setReadOnly(self, r): pass
    def isReadOnly(self): return False
    def clear(self): pass
    def setAlignment(self, a): pass
    def setValidator(self, v): pass


class QPlainTextEdit(_Widget):
    textChanged = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setPlainText(self, t): pass
    def toPlainText(self): return ""
    def appendPlainText(self, t): pass
    def clear(self): pass
    def setReadOnly(self, r): pass


class QTextEdit(_Widget):
    textChanged = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setText(self, t): pass
    def toPlainText(self): return ""
    def append(self, t): pass
    def clear(self): pass
    def setReadOnly(self, r): pass


class QSlider(_Widget):
    valueChanged = _SignalDescriptor()
    sliderMoved = _SignalDescriptor()
    sliderReleased = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setValue(self, v): pass
    def value(self): return 0
    def setMinimum(self, m): pass
    def setMaximum(self, m): pass
    def setRange(self, mn, mx): pass
    def setSingleStep(self, s): pass
    def setTickInterval(self, t): pass
    def setOrientation(self, o): pass


class QSpinBox(_Widget):
    valueChanged = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setValue(self, v): pass
    def value(self): return 0
    def setMinimum(self, m): pass
    def setMaximum(self, m): pass
    def setRange(self, mn, mx): pass
    def setSingleStep(self, s): pass
    def setSuffix(self, s): pass
    def setPrefix(self, p): pass


class QDoubleSpinBox(_Widget):
    valueChanged = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def setValue(self, v): pass
    def value(self): return 0.0
    def setMinimum(self, m): pass
    def setMaximum(self, m): pass
    def setRange(self, mn, mx): pass
    def setSingleStep(self, s): pass
    def setDecimals(self, d): pass
    def setSuffix(self, s): pass


class QComboBox(_Widget):
    currentIndexChanged = _SignalDescriptor()
    currentTextChanged = _SignalDescriptor()
    activated = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def addItem(self, *args): pass
    def addItems(self, items): pass
    def currentText(self): return ""
    def currentIndex(self): return 0
    def setCurrentIndex(self, i): pass
    def setCurrentText(self, t): pass
    def count(self): return 0
    def clear(self): pass
    def itemText(self, i): return ""


# ── Container widgets ─────────────────────────────────────────────────────────

class QFrame(_Widget):
    StyledPanel = 0x0006
    Sunken = 0x0030
    Raised = 0x0020
    Plain  = 0x0010
    Box    = 0x0001
    HLine  = 0x0004
    VLine  = 0x0005

    def setFrameShape(self, shape): pass
    def setFrameShadow(self, shadow): pass
    def setLineWidth(self, w): pass


class QSplitter(_Widget):
    def __init__(self, *args, **kwargs): pass
    def addWidget(self, w): pass
    def setSizes(self, sizes): pass
    def sizes(self): return []
    def setOrientation(self, o): pass
    def setHandleWidth(self, w): pass


class QScrollArea(_Widget):
    def __init__(self, *args, **kwargs): pass
    def setWidget(self, w): pass
    def setWidgetResizable(self, r): pass
    def widget(self): return None


class QTabWidget(_Widget):
    currentChanged = _SignalDescriptor()

    def __init__(self, *args, **kwargs): pass
    def addTab(self, widget, label): return 0
    def setCurrentIndex(self, i): pass
    def currentIndex(self): return 0
    def count(self): return 0
    def widget(self, i): return None
    def removeTab(self, i): pass


# ── Dialogs ───────────────────────────────────────────────────────────────────

class QMessageBox(_Widget):
    Ok       = 0x00000400
    Cancel   = 0x00400000
    Yes      = 0x00004000
    No       = 0x00010000
    Warning  = 2
    Critical = 3
    Information = 1
    Question = 4

    def __init__(self, *args, **kwargs): pass
    def exec(self): return self.Ok
    def setText(self, t): pass
    def setInformativeText(self, t): pass
    def setStandardButtons(self, buttons): pass
    def setDefaultButton(self, button): pass
    def setIcon(self, icon): pass
    @staticmethod
    def warning(parent, title, text, *args, **kwargs): return QMessageBox.Ok
    @staticmethod
    def critical(parent, title, text, *args, **kwargs): return QMessageBox.Ok
    @staticmethod
    def information(parent, title, text, *args, **kwargs): return QMessageBox.Ok
    @staticmethod
    def question(parent, title, text, *args, **kwargs): return QMessageBox.Yes


class QDialog(_Widget):
    Accepted = 1
    Rejected = 0

    def __init__(self, *args, **kwargs): pass
    def exec(self): return self.Accepted
    def accept(self): pass
    def reject(self): pass
    def setModal(self, m): pass


# ── Size policy ───────────────────────────────────────────────────────────────

class QSizePolicy:
    Fixed            = 0
    Minimum          = 1
    Maximum          = 4
    Preferred        = 5
    Expanding        = 7
    MinimumExpanding = 3
    Ignored          = 13

    def __init__(self, h=Preferred, v=Preferred): pass
    def setHorizontalStretch(self, s): pass
    def setVerticalStretch(self, s): pass
