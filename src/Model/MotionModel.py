import sys
import numpy as np

from Workspace.Interface.MotionCommandInterface import MotionCommandInterface


class MotionState:
    STATE_MOVE = 'state_move'
    STATE_SHOOT = 'state_shoot'
    STATE_STOP = 'state_stop'


class MotionKey:
    KEY_TRANSLATION_VECTOR = 'k_trans'
    KEY_STATE = 'k_state'
    KEY_SHOOT_VECTOR = 'k_shoot_v'


class MotionModel(MotionCommandInterface):
    def __init__(self):
        self.motion_xy: np.ndarray = np.array([0.0, 0.0])
        self.shoot_xy: np.ndarray = np.array([0.0, 1.0])
        self.state: str = MotionState.STATE_STOP

    def set_acceleration(self, percent: float) -> None:
        if not -1. <= percent <= 1.:
            self.motion_xy[0] = -1. if percent < 0 else 1.
            print('> [WARN] MotionModel.set_speed should be de percentage (-1. to 1.)',
                  file=sys.stderr)
        else:
            self.motion_xy[0] = percent

    @property
    def acceleration(self):
        return self.motion_xy[0]

    @property
    def rotation(self):
        return self.motion_xy[1]

    def set_rotation(self, percent: float) -> None:
        if not -1. <= percent <= 1.:
            self.motion_xy[1] = -1. if percent < 0 else 1.
            print('> [WARN] MotionModel.set_rotation should be de percentage (-1. to 1.)',
                  file=sys.stderr)
        else:
            self.motion_xy[1] = percent

    def shoot(self) -> None:
        self.state = MotionState.STATE_SHOOT

    def move(self) -> None:
        self.state = MotionState.STATE_MOVE

    def stop(self) -> None:
        self.state = MotionState.STATE_STOP

    def to_dict(self) -> dict:
        return {MotionKey.KEY_TRANSLATION_VECTOR: self.motion_xy.tolist(),
                MotionKey.KEY_SHOOT_VECTOR: self.shoot_xy.tolist(),
                MotionKey.KEY_STATE: self.state,
                }

    def from_dict(self, data):
        self.motion_xy = np.array(data[MotionKey.KEY_TRANSLATION_VECTOR])
        self.shoot_xy = np.array(data[MotionKey.KEY_SHOOT_VECTOR])
        self.state = data[MotionKey.KEY_STATE]
        return self

    def set_shoot_dir(self, shoot_dir: np.ndarray):
        self.shoot()
        _norm = np.linalg.norm(shoot_dir)
        if not _norm:
            self.shoot_xy = shoot_dir
        else:
            self.shoot_xy = shoot_dir / _norm
