import numpy as np
import sys

from PySide2.QtCore import QPoint, Qt, QRect
from PySide2.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QFont

from Model import ShipModel
from View.Painter.BasePainter import BasePainter, IMAGE_SHIP_PATH


class ShipPainter(BasePainter):
    def __init__(self, parent):
        BasePainter.__init__(self, parent)

    def setup(self):
        if self.is_set:
            return
        # Load ship bitmap
        self._ship_alive = QPixmap(IMAGE_SHIP_PATH)
        self._ship_alive.setMask(self._ship_alive.createMaskFromColor(QColor(0, 0, 0)))

        self._ship_dead = self._ship_alive.copy()

        _comon_color = QPixmap(self._ship_alive.size())
        _comon_color.fill(QColor(0, 255, 0))
        _comon_color.setMask(self._ship_alive.createMaskFromColor(QColor(255, 255, 255), mode=Qt.MaskOutColor))

        _dead_color = QPixmap(self._ship_dead.size())
        _dead_color.fill(QColor(100, 100, 100))
        _dead_color.setMask(self._ship_dead.createMaskFromColor(QColor(255, 255, 255), mode=Qt.MaskOutColor))

        painter = QPainter(self._ship_alive)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(QPoint(0, 0), _comon_color)
        painter.end()

        painter = QPainter(self._ship_dead)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(QPoint(0, 0), _dead_color)
        painter.end()

        self._ship_alive = self._ship_alive.scaledToHeight(50, mode=Qt.SmoothTransformation)
        self._ship_dead = self._ship_dead.scaledToHeight(50, mode=Qt.SmoothTransformation)

        self._life_bar_width = int(self._ship_alive.width())
        self._life_bar_xy = np.array([self._life_bar_width // 2, self._ship_alive.height() // 2 + 25])
        self._life_bar_height = 2
        self.debug = 0
        self.is_set = True

    def paint(self, painter: QPainter, model: ShipModel = None):
        assert self.is_set, 'Painter is not set'

        # Draw ship
        if model.is_alive:
            _ship = self._ship_alive
        else:
            _ship = self._ship_dead

        _pixmap = _ship.transformed(model.transform, mode=Qt.SmoothTransformation)
        _center_ship = self.transform(model.x - _pixmap.width()/2, model.y + _pixmap.height()/2, is_point=True)

        if 0 <= _center_ship.x() <= self.parent.width() and 0 <= _center_ship.y() <= self.parent.height():
            painter.drawPixmap(_center_ship, _pixmap)

            # Draw life bar
            _center_bar = self.transform(model.x - self._life_bar_xy[0], model.y + self._life_bar_xy[1], is_point=True)
            painter.setPen(QPen(QColor(255, 0, 0), 0, Qt.NoPen))
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawRect(_center_bar.x(), _center_bar.y(), self._life_bar_width, 5)
            painter.setBrush(QBrush(QColor(0, 255, 0)))
            painter.drawRect(_center_bar.x(), _center_bar.y(), int(self._life_bar_width * model.life), 5)
            painter.setPen(QPen(QColor(*model.color), 5, Qt.SolidLine))
            _center_title = self.transform(model.x - 100, model.y + 70, is_point=True)
            painter.setFont(QFont('Open Sans', weight=QFont.Normal, pointSize=8))
            painter.drawText(QRect(_center_title.x(), _center_title.y(),
                                   200, 25), Qt.AlignHCenter | Qt.AlignTop, '<{}>'.format(model.name))
            painter.setBrush(QBrush(QColor(*model.color)))
            _center_point = self.transform(model.x, model.y, is_point=True)
            painter.drawPoint(_center_point)
        else:
            _xy = QPoint(_center_ship)
            if _center_ship.x() < 0:
                _xy.setX(0)
            if self.parent.width() < _center_ship.x():
                _xy.setX(self.parent.width())

            if _center_ship.y() < 0:
                _xy.setY(0)
            if self.parent.height() < _center_ship.y():
                _xy.setY(self.parent.height())

            painter.setPen(QPen(QColor(0, 0, 0), 30, Qt.SolidLine, Qt.RoundCap))
            painter.drawPoint(_xy)
            painter.setPen(QPen(QColor(*model.color), 25, Qt.SolidLine, Qt.RoundCap))
            painter.drawPoint(_xy)
