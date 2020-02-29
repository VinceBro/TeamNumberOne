import numpy as np

from Model.BaseModel import BaseModel
from Model.ModelType import ModelType as mode_t


class BoltModel(BaseModel):
    def __init__(self, creator: str = 'unknow', pst_xy: np.ndarray = None, dir_xy: np.ndarray = None, v_xy: np.ndarray = None):
        BaseModel.__init__(self, mode_t.BOLT_MODEL, pst_xy, dir_xy, v_xy, life=.01, radius=5, weight=10,
                           damage=0.05, creator=creator)
        self.name = 'bolt'

