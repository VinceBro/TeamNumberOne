from Model.MotionModel import MotionModel
from Workspace.BaseWorkspace import BaseWorkspace


class myWorkspace(BaseWorkspace):
    def __init__(self, controller):
        BaseWorkspace.__init__(self, controller)
        self.counter = 0

    def loop(self):
        _motion = MotionModel()
        if self.ctrl.wait_until_event():
            self.counter += 1
            _my_ship = self.ctrl.get_player(self.ctrl.get_name())
            _players = self.ctrl.get_data_from_players(enemy_only=True)
            _dist, _nearest = self.ctrl.get_the_nearest_mob(_my_ship.xy, _players)
            if _nearest is not None:
                _dir_to_shoot = self.ctrl.get_direction_between(_my_ship, _nearest)
                _motion.shoot()
                _motion.set_shoot_dir(_dir_to_shoot)
            self.ctrl.set_motion_command(_motion)
