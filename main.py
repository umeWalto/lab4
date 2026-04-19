import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QColor, QPainter, QPolygon
from PyQt6.QtCore import QPoint


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

class Circle(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.r = 30

    def draw(self, painter):
        painter.setBrush(self._color)
        painter.drawEllipse(self._x - self.r, self._y - self.r, self.r * 2, self.r * 2)

    def contains(self, x, y):
        return (x - self._x) ** 2 + (y - self._y) ** 2 <= self.r ** 2


class Square(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 50

    def draw(self, painter):
        painter.setBrush(self._color)
        painter.drawRect(self._x, self._y, self.size, self.size)

    def contains(self, x, y):
        return self._x <= x <= self._x + self.size and self._y <= y <= self._y + self.size


class Triangle(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 50

    def draw(self, painter):
        painter.setBrush(self._color)
        points = QPolygon([
            QPoint(self._x, self._y),
            QPoint(self._x + self.size, self._y),
            QPoint(self._x + self.size // 2, self._y - self.size)
        ])
        painter.drawPolygon(points)

    def contains(self, x, y):
        return self._x <= x <= self._x + self.size and self._y - self.size <= y <= self._y

app = QApplication(sys.argv)
w = QWidget()
w.show()
sys.exit(app.exec())