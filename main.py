import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog
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

class MyStorage:
    def __init__(self):
        self._data = []

    def add(self, obj):
        self._data.append(obj)

    def draw_all(self, painter):
        for o in self._data:
            o.draw(painter)

    def clear_selection(self):
        for o in self._data:
            o.set_selected(False)

    def selected(self):
        return [o for o in self._data if o.is_selected()]

    def remove_selected(self):
        self._data = [o for o in self._data if not o.is_selected()]

class Canvas(QWidget):
    def __init__(self, storage):
        super().__init__()
        self.storage = storage

    def mousePressEvent(self, e):
        x, y = int(e.position().x()), int(e.position().y())

        for obj in reversed(self.storage._data):
            if obj.contains(x, y):
                obj.set_selected(True)
                self.update()
                return

        self.storage.add(Circle(x, y))
        self.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Delete:
            self.storage.remove_selected()

        elif e.key() == Qt.Key.Key_C:
            color = QColorDialog.getColor()
            if color.isValid():
                for o in self.storage.selected():
                    o.set_color(color)

    self.canvas.update()

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.dragging = None
        self.last_pos = None

    def mousePressEvent(self, e):
        x, y = int(e.position().x()), int(e.position().y())

        for obj in reversed(self.storage._data):
            if obj.contains(x, y):
                self.dragging = obj
                self.last_pos = (x, y)
                obj.set_selected(True)
                return

    def mouseMoveEvent(self, e):
        if self.dragging:
            x, y = int(e.position().x()), int(e.position().y())
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]

            self.dragging.move(dx, dy, self.width(), self.height())
            self.last_pos = (x, y)
            self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor")

        self.storage = MyStorage()
        self.canvas = Canvas(self.storage)

        layout = QVBoxLayout()

        toolbar = QHBoxLayout()
        for name in ["circle", "square", "triangle"]:
            btn = QPushButton(name)
            toolbar.addWidget(btn)

        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
storage = MyStorage()
canvas = Canvas(storage)
canvas.show()