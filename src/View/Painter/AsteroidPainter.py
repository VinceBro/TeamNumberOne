from PySide2.QtGui import QPixmap, QPainter, QTransform
from PySide2.QtCore import Qt

from Model import BaseModel
from View.Painter.BasePainter import BasePainter, IMAGE_ASTEROID_PATH


class AsteroidPainter(BasePainter):
    def __init__(self, parent):
        BasePainter.__init__(self, parent)
        self._pixel_map = QPixmap(IMAGE_ASTEROID_PATH)
        self._pixel_map.setMask(self._pixel_map.createHeuristicMask())
        self._pixel_map = self._pixel_map.copy(0, 0, 500, 500)
        self._pixel_map = self._pixel_map.scaledToHeight(256, mode=Qt.SmoothTransformation)

    def setup(self):
        pass

    def paint(self, painter: QPainter, model: BaseModel = None):
        _pix_map = self._pixel_map.scaledToHeight(model.radius*1.025, mode=Qt.SmoothTransformation)
        _seed = hash(model.name)
        _transf = QTransform()
        _transf.rotate(_seed % 360)
        _pix_map = _pix_map.transformed(_transf, mode=Qt.SmoothTransformation)
        _x, _y = self.transform(model.x - _pix_map.width()/2.0, model.y + _pix_map.height()/2.0)
        painter.drawPixmap(round(_x), round(_y), _pix_map)
