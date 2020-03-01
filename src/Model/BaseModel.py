import numpy as np
from PySide2.QtGui import QTransform
from Model.ModelType import ModelType
from Workspace.Interface.MobileObjectInterface import MobileObjectInterface


class BaseModel(MobileObjectInterface):
    def __init__(self, model_type: str = '', pst_xy: np.ndarray = None, dir_xy: np.ndarray = None, v_xy: np.ndarray = None,
                 radius: int = 1, damage: float = 0, life: float = 1, weight: float = 1, creator: str = 'unknown'):
        self._type = model_type
        self._pst_xy = np.array([0, 0]) if pst_xy is None else pst_xy
        self._dir_xy = np.array([0, 1]) if dir_xy is None else dir_xy
        self._v_xy = np.array([0, 0]) if v_xy is None else v_xy
        self._transform = QTransform()
        self._transform.rotate(self.angle)

        self._damage = damage
        self._radius = radius
        self._life = life
        self.color = 255, 255, 255
        self.weight = weight
        self.name = 'unknown'
        self._creator = creator

    def set_damage(self, life_point):
        if self.is_alive:
            self._life -= life_point
            if self._life < 0:
                self._life = 0
                self.color = 100, 100, 100

    @property
    def life(self) -> float:
        return self._life

    @property
    def creator(self) -> str:
        return self._creator

    @property
    def is_alive(self) -> bool:
        return self._life > 0

    @property
    def damage(self) -> float:
        return self._damage

    @property
    def type(self) -> str:
        return self._type

    @property
    def radius(self) -> int:
        return self._radius

    @property
    def x(self) -> float:
        return self._pst_xy[0]

    @property
    def y(self) -> float:
        return self._pst_xy[1]

    @property
    def position(self) -> np.ndarray:
        return np.array(self._pst_xy)

    @property
    def xy(self) -> np.ndarray:
        return np.array(self._pst_xy)

    @property
    def dir(self) -> np.ndarray:
        return np.array(self._dir_xy)

    @property
    def angle(self) -> float:
        return 180 * np.arctan2(self.dir_y, self.dir_x) / np.pi

    def set_angle(self, angle) -> None:
        self._transform = QTransform()
        self._transform.rotate(angle)
        self.set_dir(np.array([self._transform.m11(), self._transform.m12()]))

    @property
    def transform(self) -> QTransform:
        return self._transform

    @property
    def dir_x(self) -> float:
        return self._dir_xy[1]

    @property
    def dir_y(self) -> float:
        return self._dir_xy[0]

    @property
    def speed(self) -> np.ndarray:
        return np.array(self._v_xy)

    def set_position(self, pst_xy: np.ndarray) -> None:
        self._pst_xy = pst_xy

    def set_dir(self, dir_xy: np.ndarray) -> None:
        self._dir_xy = dir_xy

    def set_speed(self, v_xy: np.ndarray) -> None:
        self._v_xy = v_xy

    def get_propulsion_speed(self) -> float:
        return self._v_xy[0]

    def get_rotation_speed(self) -> float:
        return self._v_xy[1]

    def to_dict(self) -> dict:
        return {ModelType.KEY_TYPE: self._type,
                ModelType.KEY_POSITION: self._pst_xy.tolist(),
                ModelType.KEY_DIRECTION: self._dir_xy.tolist(),
                ModelType.KEY_SPEED: self._v_xy.tolist(),
                ModelType.KEY_LIFE: self._life,
                ModelType.KEY_COLOR: self.color,
                ModelType.KEY_NAME: self.name,
                ModelType.KEY_DAMAGE: self.damage,
                ModelType.KEY_RADIUS: self.radius,
                ModelType.KEY_WEIGTH: self.weight,
                ModelType.KEY_CREATOR: self._creator,
                }

    def from_dict(self, data):
        self._type = data[ModelType.KEY_TYPE]
        self._pst_xy = np.array(data[ModelType.KEY_POSITION])
        self._dir_xy = np.array(data[ModelType.KEY_DIRECTION])
        self._v_xy = np.array(data[ModelType.KEY_SPEED])
        self._life = data[ModelType.KEY_LIFE]
        self.color = data[ModelType.KEY_COLOR]
        self.name = data[ModelType.KEY_NAME]
        self._damage = data[ModelType.KEY_DAMAGE]
        self._radius = data[ModelType.KEY_RADIUS]
        self.weight = data[ModelType.KEY_WEIGTH]
        self.set_angle(self.angle)
        self._creator = data[ModelType.KEY_CREATOR]
        return self

    def __str__(self) -> str:
        return 'pst: {} / dir: {} / speed: {}'.format(self._pst_xy,
                                                      self._dir_xy,
                                                      self._v_xy,
                                                      )
