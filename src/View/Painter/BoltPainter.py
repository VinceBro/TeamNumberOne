from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QPen, QColor, QPainter

from Model.BaseModel import BaseModel
from View.Painter.BasePainter import BasePainter


class BoltPainter(BasePainter):
    def __init__(self, parent):
        BasePainter.__init__(self, parent)
        self._pen_z_1 = None
        self._pen_z_2 = None
        self._pen_z_0 = None
        self._length = None

    def setup(self):
        if self.is_set:
            return

        self._pen_z_2 = QPen(QColor(255, 0, 0), 5, Qt.SolidLine)
        self._pen_z_2.setCapStyle(Qt.RoundCap)
        self._pen_z_1 = QPen(QColor(255, 100, 100), 5, Qt.SolidLine)
        self._pen_z_1.setCapStyle(Qt.RoundCap)
        self._pen_z_0 = QPen(QColor(255, 255, 255), 5, Qt.SolidLine)
        self._pen_z_0.setCapStyle(Qt.RoundCap)
        self._length = 25
        self.is_set = True

    def paint(self, painter: QPainter, model: BaseModel):
        if model.is_alive:
            assert self.is_set, 'Painter is not set.'
            _origin = self.transform(model.x, model.y, is_point=True)
            for _i, _pen in enumerate([self._pen_z_2, self._pen_z_1, self._pen_z_0]):
                _factor = (3 - _i) / 3
                _tail_x = _origin.x() - model.dir_y * self._length * _factor
                _tail_y = _origin.y() + model.dir_x * self._length * _factor
                _tail = QPoint(_tail_x, _tail_y)
                painter.setPen(_pen)
                painter.drawLine(_origin, _tail)
