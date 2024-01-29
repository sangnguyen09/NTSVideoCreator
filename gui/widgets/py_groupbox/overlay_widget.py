from typing import Tuple

from PySide6.QtCore import QRect, Qt, QEvent
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QWidget


class TextOverlayWidget(QWidget):
    def __init__(
            self,
            parent: QWidget,
            text: str,
            overlay_width: int = 300,
            overlay_height: int = 150,
            font_size: int = 20,
    ):
        super().__init__(parent)

        self._text = text
        self._font_size = font_size
        self.is_showing = False

        self._overlay_width = overlay_width
        self._overlay_height = overlay_height

        self._TRANSPARENT_COLOR = QColor(0, 0, 0, 0)
        self._WINDOW_BACKGROUND_COLOR = QColor(25, 25, 25, 125)
        self._OVERLAY_BACKGROUND_COLOR = self.palette().color(QPalette.Base)

        parent.installEventFilter(self)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self._resize_to_parent()

    def update_text(self,text):
        self._text = text
        self.repaint()
        
    def start(self):
        self.is_showing = True
        self.show()
        
    def stop(self):
        self.is_showing = False
    
        self.hide()
        
    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Resize:
            self._resize_to_parent()

        return super().eventFilter(obj, event)

    def _resize_to_parent(self):
        self.move(0, 0)
        self.resize(self.parent().width(), self.parent().height())

        overlay_corner_width, overlay_corner_height = self._get_overlay_corner()


    def _get_window_size(self) -> Tuple[int, int]:
        size = self.size()
        return size.width(), size.height()

    def _get_overlay_corner(self) -> Tuple[int, int]:
        width, height = self._get_window_size()
        overlay_corner_width = int(width / 2 - self._overlay_width / 2)
        overlay_corner_height = int(height / 2 - self._overlay_height / 2)
        return overlay_corner_width, overlay_corner_height

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(self._TRANSPARENT_COLOR)
        painter.setBrush(self._WINDOW_BACKGROUND_COLOR)
        width, height = self._get_window_size()
        painter.drawRect(0, 0, width, height)

        painter.setPen(self._TRANSPARENT_COLOR)
        painter.setBrush(self._OVERLAY_BACKGROUND_COLOR)
        rounding_radius = 5
        overlay_rectangle = QRect(
            *self._get_overlay_corner(), self._overlay_width, self._overlay_height
        )
        painter.drawRoundedRect(overlay_rectangle, rounding_radius, rounding_radius)

        font = self.font()
        font.setPixelSize(self._font_size)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(overlay_rectangle, Qt.AlignCenter, self._text)

        painter.end()

    def mouseDoubleClickEvent (self, e):
        self.hide()