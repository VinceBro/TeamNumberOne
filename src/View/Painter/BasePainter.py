import abc
import sys

from PySide2.QtGui import QPainter

from Model.BaseModel import BaseModel

IMAGE_PATH_PREFIX = '' if sys.platform == 'win32' else '../'
IMAGE_ROOT_PATH = IMAGE_PATH_PREFIX + 'Image/'
IMAGE_SHIP_PATH = IMAGE_ROOT_PATH + 'spaceship.png'
IMAGE_ASTEROID_PATH = IMAGE_ROOT_PATH + 'asteroid.png'
IMAGE_GALAXY_PATH = IMAGE_ROOT_PATH + 'galaxy_map.png'

class BasePainter:
    _transf = None

    def __init__(self, parent=None):
        self.is_set = False
        self.parent = parent

    @property
    def transform(self):
        return BasePainter._transf

    @abc.abstractmethod
    def paint(self, painter: QPainter, model: BaseModel):
        pass

    @abc.abstractmethod
    def setup(self):
        pass

    def set_transform(self, transf_func):
        BasePainter._transf = transf_func
