"""Stub for PyQt6.QtGui — no-op stand-ins for all names used across waxx/k-exp."""


class QColor:
    def __init__(self, *args, **kwargs): pass
    def setAlpha(self, alpha): pass
    def name(self): return "#000000"
    def red(self): return 0
    def green(self): return 0
    def blue(self): return 0
    def alpha(self): return 255
    def isValid(self): return True
    @staticmethod
    def fromRgb(r, g, b, a=255): return QColor()
    @staticmethod
    def fromHsv(h, s, v, a=255): return QColor()


class QFont:
    def __init__(self, *args, **kwargs): pass
    def setPointSize(self, size): pass
    def setPixelSize(self, size): pass
    def setBold(self, bold): pass
    def setItalic(self, italic): pass
    def setWeight(self, weight): pass
    def pointSize(self): return 10
    def family(self): return ""


class QIcon:
    def __init__(self, *args, **kwargs): pass
    def isNull(self): return True
    def pixmap(self, *args, **kwargs): return QPixmap()


class QImage:
    Format_Grayscale8 = 12
    Format_RGB32 = 4
    Format_ARGB32 = 5
    Format_RGB888 = 13

    def __init__(self, *args, **kwargs): pass
    def width(self): return 0
    def height(self): return 0
    def isNull(self): return True
    def convertToFormat(self, fmt): return self
    def bits(self): return b""
    def bytesPerLine(self): return 0


class QPixmap:
    def __init__(self, *args, **kwargs): pass
    def isNull(self): return True
    def width(self): return 0
    def height(self): return 0
    def scaled(self, *args, **kwargs): return self
    @staticmethod
    def fromImage(image, flags=None): return QPixmap()


class QPainter:
    def __init__(self, *args, **kwargs): pass
    def begin(self, device): return True
    def end(self): return True
    def __enter__(self): return self
    def __exit__(self, *args): self.end()
    def setPen(self, pen): pass
    def setBrush(self, brush): pass
    def setFont(self, font): pass
    def drawText(self, *args, **kwargs): pass
    def drawLine(self, *args, **kwargs): pass
    def drawRect(self, *args, **kwargs): pass
    def drawEllipse(self, *args, **kwargs): pass
    def drawImage(self, *args, **kwargs): pass
    def drawPixmap(self, *args, **kwargs): pass
    def fillRect(self, *args, **kwargs): pass
    def setOpacity(self, opacity): pass
    def setRenderHint(self, hint, on=True): pass
    def translate(self, *args): pass
    def rotate(self, angle): pass
    def scale(self, sx, sy): pass
    def save(self): pass
    def restore(self): pass

    class RenderHint:
        Antialiasing = 0x01
        TextAntialiasing = 0x02
        SmoothPixmapTransform = 0x04


class QPen:
    def __init__(self, *args, **kwargs): pass
    def setWidth(self, width): pass
    def setColor(self, color): pass
    def setStyle(self, style): pass
    def width(self): return 1


class QBrush:
    def __init__(self, *args, **kwargs): pass
    def setColor(self, color): pass
    def setStyle(self, style): pass
    def color(self): return QColor()


class QPaintEvent:
    def __init__(self, *args, **kwargs): pass
    def rect(self):
        from PyQt6.QtCore import QRect
        return QRect()


class QPalette:
    Window       = 10
    WindowText   = 0
    Base         = 9
    AlternateBase = 16
    Text         = 6
    Button       = 1
    ButtonText   = 8
    Highlight    = 12
    HighlightedText = 13

    def __init__(self, *args, **kwargs): pass
    def setColor(self, *args, **kwargs): pass
    def color(self, *args, **kwargs): return QColor()


class QGuiApplication:
    def __init__(self, *args, **kwargs): pass
    @staticmethod
    def instance(): return None
    @staticmethod
    def screens(): return []
    @staticmethod
    def primaryScreen(): return QScreen()
    @staticmethod
    def setWindowIcon(icon): pass


class QScreen:
    def __init__(self, *args, **kwargs): pass
    def geometry(self):
        from PyQt6.QtCore import QRect
        return QRect(0, 0, 1920, 1080)
    def availableGeometry(self):
        from PyQt6.QtCore import QRect
        return QRect(0, 0, 1920, 1080)
    def size(self):
        from PyQt6.QtCore import QSize
        return QSize(1920, 1080)
