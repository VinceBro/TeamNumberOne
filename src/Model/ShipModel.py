import numpy as np

from Model.BaseModel import BaseModel
from Model.ModelType import ModelType


class ShipModel(BaseModel):
    def __init__(self, pst_xy: np.ndarray = None, dir_xy: np.ndarray = None, v_xy: np.ndarray = None):
        BaseModel.__init__(self, ModelType.SHIP_MODEL, pst_xy, dir_xy, v_xy, life=1., radius=40, weight=100,
                           damage=.1)
