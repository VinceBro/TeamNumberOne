import numpy as np
from PySide2.QtGui import QPen, QColor, QPainter, QRadialGradient, QPixmap
from PySide2.QtCore import Qt, QSize, QPoint

from Model.PartyModel import PartyConst
from Model.BaseModel import BaseModel
from View.Painter.BasePainter import BasePainter, IMAGE_GALAXY_PATH


class BackgroundPainter(BasePainter):

    def __init__(self, parent):
        BasePainter.__init__(self, parent)
        self._galaxy = QPixmap(IMAGE_GALAXY_PATH)
        if self._galaxy.size() != QSize(PartyConst.WIDTH, PartyConst.HEIGHT):
            self._galaxy = QPixmap(QSize(PartyConst.WIDTH, PartyConst.HEIGHT))
            self._galaxy.fill(QColor('#20124d'))
        else:
            self.is_set = True

    def setup(self):
        if not self.is_set:
            _edge = max([PartyConst.WIDTH, PartyConst.HEIGHT])
            self._stars = np.random.randint(low=0, high=_edge, size=((_edge // 250) ** 2, 2))
            self._pen_link = QPen(QColor('#351c75'), 2, Qt.SolidLine)
            self._lines = []
            min_dist = 100
            for _star in self._stars:
                for _sub_star in self._stars:
                    if 0 < np.linalg.norm(_star-_sub_star) < min_dist:
                        self._lines.append((_star, _sub_star))

            _edge = max([PartyConst.WIDTH, PartyConst.HEIGHT])

            _center = QPoint(self._galaxy.width()//2, self._galaxy.height()//2)
            _gradient = QRadialGradient(_center, _edge // 2)
            _gradient.setColorAt(1, QColor('#20124d'))
            _gradient.setColorAt(0, QColor('#351c75'))

            painter = QPainter(self._galaxy)
            painter.fillRect(0, 0,
                             _edge, _edge, _gradient)

            painter.setPen(self._pen_link)
            for _xy1, _xy2 in self._lines:
                _xy1, _xy2 = QPoint(*_xy1), QPoint(*_xy2)
                painter.drawLine(_xy1, _xy2)

            _star_pens = [QPen(QColor('#ffffff'), _size, Qt.SolidLine) for _size in [1, 2, 3, 4]]
            for _i, (_x, _y) in enumerate(self._stars):
                _xy = QPoint(_x, _y)
                painter.setPen(_star_pens[_i % len(_star_pens)])
                painter.drawPoint(_xy)
            painter.end()
            self._galaxy.save(IMAGE_GALAXY_PATH)
            self.is_set = True

    def paint(self, painter: QPainter, model: BaseModel = None):
        _xy = self.transform(-self._galaxy.width()//2, self._galaxy.height()//2, is_point=True)
        painter.drawPixmap(_xy, self._galaxy)
