from Model.MotionModel import MotionModel
from Workspace.BaseWorkspace import BaseWorkspace
from Controller.ClientController import ClientController
from Workspace.NavigationClass import NavigationMethods as nm


class myWorkspace(BaseWorkspace):
    def __init__(self, controller):
        BaseWorkspace.__init__(self, controller)
        self.counter = 0
        self.radius = 750
        self.sauce = True

    def loop(self):
        _motion = MotionModel()
        if self.ctrl.wait_until_event():
            self.my_ship = self.ctrl.get_player(self.ctrl.get_name())
            _players = self.ctrl.get_data_from_players(enemy_only=True)
            _dist, _nearest = self.ctrl.get_the_nearest_mob(self.my_ship.xy, _players)
            if (self.counter > 0 and self.counter < 50): 
                _motion.set_rotation(-1.0)
                _motion.move()
            elif (self.counter > 50 and self.counter < 100): 
                _motion.set_acceleration(1)
                _motion.move()
            elif (dans la deadzone):
                if (self.sauce):
                    _motion.set_acceleration(1)
                    _motion.move()
                    self.sauce = False
                else:
                    _motion.set_rotation(-1.0)
                    _motion.move()
                    self.sauce = True


            elif _nearest is not None:
                _dir_to_shoot = self.ctrl.get_direction_between(self.my_ship, _nearest)
                _motion.shoot()
                _motion.set_shoot_dir(_dir_to_shoot)
            self.counter += 1
            # objects_in_radius = nm.getObjectsInRadiusOfMe(self.ctrl, self.my_ship, self.radius)
            # asteroids_in_radius = nm.getAsteroidsInRadius(self.ctrl, objects_in_radius)
            # asteroid_resulting_vector = nm.getAsteroidResultingVector(self.ctrl,self.my_ship, asteroids_in_radius)
            # print(asteroid_resulting_vector)
            # _ = nm.moveShipAccordingToVector(self.ctrl, self.my_ship, asteroid_resulting_vector)            
            self.ctrl.set_motion_command(_motion)

            




