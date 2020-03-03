import numpy as np
from Model.MotionModel import MotionModel
from Workspace.BaseWorkspace import BaseWorkspace
from Controller.ClientController import ClientController
from Workspace.NavigationClass import NavigationMethods as nm


class myWorkspace(BaseWorkspace):
    def __init__(self, controller):
        BaseWorkspace.__init__(self, controller)
        self.counter = 0
        self.deadzone_counter = 0
        self.radius = 750
        self.sauce = True
        self.constant_speed = 300
        self.deadzone_offset = 400

    def loop(self):
        _motion = MotionModel()
        if self.ctrl.wait_until_event():
            self.my_ship = self.ctrl.get_player(self.ctrl.get_name())
            _players = self.ctrl.get_data_from_players(enemy_only=True)
            _dist, _nearest = self.ctrl.get_the_nearest_mob(self.my_ship.xy, _players)
            objects_in_radius = nm.getObjectsInRadiusOfMe(self.ctrl, self.my_ship, self.radius)
            asteroids_in_radius = nm.getAsteroidsInRadius(self.ctrl, objects_in_radius)
            print(f"asteroids in radius : {asteroids_in_radius}")
            if (nm.checkIfInDeadzone(self.ctrl, self.my_ship, self.deadzone_offset)):
                nm.getDeadZoneOrthogonalResultingVector(self.ctrl, self.my_ship)
                deadzone_vector = nm.getDeadZoneResultingVector(self.ctrl, self.my_ship)
                nm.moveShipAccordingToVector(self.ctrl,self.my_ship,_motion,deadzone_vector)
                _motion.move()
            elif self.my_ship.get_propulsion_speed() < self.constant_speed:
                _motion.set_acceleration(1.0)
                _motion.move()
            elif asteroids_in_radius != []:
                asteroid_resulting_vector = nm.getAsteroidResultingVector(self.ctrl,self.my_ship, asteroids_in_radius)
                nm.moveShipAccordingToVector(self.ctrl, self.my_ship, _motion, asteroid_resulting_vector)
                _motion.move()
            elif _nearest is not None:
                _dir_to_shoot = self.ctrl.get_direction_between(self.my_ship, _nearest)
                _motion.shoot()
                _motion.set_shoot_dir(_dir_to_shoot)

            self.counter += 1
            print(self.counter)

            self.ctrl.set_motion_command(_motion)

            




