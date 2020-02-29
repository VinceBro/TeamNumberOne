import numpy as np

from Model.BaseModel import BaseModel
from Model.ModelType import ModelType


class AsteroidModel(BaseModel):
    id = 0

    def __init__(self, pst_xy: np.ndarray = None, dir_xy: np.ndarray = None, v_xy: np.ndarray = None, radius: int=120):
        BaseModel.__init__(self, ModelType.ASTEROID_MODEL, pst_xy, dir_xy, v_xy, life=1e8, damage=.025, radius=radius,
                           weight=radius*10)
        AsteroidModel.id += 1
        self.name = 'asteroid{}'.format(AsteroidModel.id)
