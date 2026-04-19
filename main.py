import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QColorDialog
)
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygon
from PyQt6.QtCore import Qt, QPoint

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
        painter.setBrush(self._color if not self._selected else QColor(255, 100, 100))
        painter.drawEllipse(self._x - self.r, self._y - self.r, self.r * 2, self.r * 2)

    def contains(self, x, y):
        return (x - self._x) ** 2 + (y - self._y) ** 2 <= self.r ** 2

    def resize(self, delta):
        self.r = max(5, self.r + delta)

    def clamp(self, w, h):
        self._x = max(self.r, min(self._x, w - self.r))
        self._y = max(self.r, min(self._y, h - self.r))

class Square(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 50

    def draw(self, painter):
        painter.setBrush(self._color if not self._selected else QColor(255, 100, 100))
        painter.drawRect(self._x, self._y, self.size, self.size)

    def contains(self, x, y):
        return self._x <= x <= self._x + self.size and self._y <= y <= self._y + self.size

    def resize(self, delta):
        self.size = max(10, self.size + delta)

    def clamp(self, w, h):
        self._x = max(0, min(self._x, w - self.size))
        self._y = max(0, min(self._y, h - self.size))

class Triangle(Shape):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 50

    def draw(self, painter):
        painter.setBrush(self._color if not self._selected else QColor(255, 100, 100))
        points = QPolygon([
            QPoint(self._x, self._y),
            QPoint(self._x + self.size, self._y),
            QPoint(self._x + self.size // 2, self._y - self.size)
        ])
        painter.drawPolygon(points)

    def contains(self, x, y):
        return self._x <= x <= self._x + self.size and self._y - self.size <= y <= self._y

    def resize(self, delta):
        self.size = max(10, self.size + delta)

    def clamp(self, w, h):
        self._x = max(0, min(self._x, w - self.size))
        self._y = max(self.size, min(self._y, h))

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

    def remove_selected(self):
        self._data = [o for o in self._data if not o.is_selected()]

    def selected(self):
        return [o for o in self._data if o.is_selected()]

class Canvas(QWidget):
    def __init__(self, storage, parent):
        super().__init__()
        self.storage = storage
        self.parent = parent
        self.dragging = None
        self.last_pos = None

    def paintEvent(self, e):
        painter = QPainter(self)
        self.storage.draw_all(painter)

    def mousePressEvent(self, e):
        x, y = int(e.position().x()), int(e.position().y())
        ctrl = QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier

        clicked = None
        for obj in reversed(self.storage._data):
            if obj.contains(x, y):
                clicked = obj
                break

        if not ctrl:
            self.storage.clear_selection()

        if clicked:
            clicked.set_selected(True)
            self.dragging = clicked
            self.last_pos = (x, y)
        else:
            tool = self.parent.current_tool
            if tool == "circle":
                self.storage.add(Circle(x, y))
            elif tool == "square":
                self.storage.add(Square(x, y))
            elif tool == "triangle":
                self.storage.add(Triangle(x, y))

        self.update()

    def mouseMoveEvent(self, e):
        if self.dragging:
            x, y = int(e.position().x()), int(e.position().y())
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]

            for obj in self.storage.selected():
                obj.move(dx, dy, self.width(), self.height())

            self.last_pos = (x, y)
            self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор")
        self.resize(900, 600)

        self.storage = MyStorage()
        self.current_tool = "circle"

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout()

        toolbar = QHBoxLayout()
        for name in ["circle", "square", "triangle"]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: setattr(self, "current_tool", n))
            toolbar.addWidget(btn)

        layout.addLayout(toolbar)

        self.canvas = Canvas(self.storage, self)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Delete:
            self.storage.remove_selected()

        elif e.key() == Qt.Key.Key_C:
            color = QColorDialog.getColor()
            if color.isValid():
                for o in self.storage.selected():
                    o.set_color(color)

        elif e.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            for o in self.storage.selected():
                o.resize(5)

        elif e.key() == Qt.Key.Key_Minus:
            for o in self.storage.selected():
                o.resize(-5)

        self.canvas.update()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())