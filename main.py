import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QColor


class Shape:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._selected = False
        self._color = QColor(100, 200, 255)

    def draw(self, painter):
        raise NotImplementedError()

    def contains(self, x, y):
        raise NotImplementedError()

    def move(self, dx, dy, w, h):
        self._x += dx
        self._y += dy
        self.clamp(w, h)

    def clamp(self, w, h):
        self._x = max(0, min(self._x, w))
        self._y = max(0, min(self._y, h))

    def resize(self, delta):
        pass

    def set_selected(self, val):
        self._selected = val

    def is_selected(self):
        return self._selected

    def set_color(self, color):
        self._color = color


app = QApplication(sys.argv)
w = QWidget()
w.show()
sys.exit(app.exec())