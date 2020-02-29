from Model.MotionModel import MotionModel
from Workspace.BaseWorkspace import BaseWorkspace
from Controller.ClientController import ClientController
from Workspace.NavigationClass import NavigationMethods as nm


class myWorkspace(BaseWorkspace):
    def __init__(self, controller):
        BaseWorkspace.__init__(self, controller)
        self.counter = 0
        self.radius = 750

    def loop(self):
        _motion = MotionModel()
        if self.ctrl.wait_until_event():
            self.counter += 1
            self.my_ship = self.ctrl.get_player(self.ctrl.get_name())
            objects_in_radius = nm.getObjectsInRadiusOfMe(self.ctrl, self.my_ship, self.radius)
            asteroids_in_radius = nm.getAsteroidsInRadius(self.ctrl, objects_in_radius)
            asteroid_resulting_vector = nm.getAsteroidResultingVector(self.ctrl,self.my_ship, asteroids_in_radius)
            print(asteroid_resulting_vector)
            # _ = nm.moveShipAccordingToVector(self.ctrl, self.my_ship, asteroid_resulting_vector)            

            

            # _players = self.ctrl.get_data_from_players(enemy_only=True)
            # _dist, _nearest = self.ctrl.get_the_nearest_mob(_my_ship.xy, _players)
            # if _nearest is not None:
            #     _dir_to_shoot = self.ctrl.get_direction_between(_my_ship, _nearest)
            #     _motion.shoot()
            #     _motion.set_shoot_dir(_dir_to_shoot)
            # self.ctrl.set_motion_command(_motion)



