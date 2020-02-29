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

    def loop(self):
        _motion = MotionModel()
        if self.ctrl.wait_until_event():
            self.my_ship = self.ctrl.get_player(self.ctrl.get_name())
            _players = self.ctrl.get_data_from_players(enemy_only=True)
            _dist, _nearest = self.ctrl.get_the_nearest_mob(self.my_ship.xy, _players)
            if (self.counter > 0 and self.counter < 50): 
                _motion.set_rotation(-1.0)
                _motion.move()
            elif (self.counter > 50 and self.counter < 100) or self.counter % 50 == 0: 
                _motion.set_acceleration(1)
                _motion.move()
            elif (nm.checkIfInDeadzone(self.ctrl, self.my_ship)):
                if self.deadzone_counter < 80:
                    _motion.set_acceleration(1)
                    _motion.set_rotation(0.8)

                    
                    #t'es stuck
                    
                    
                self.deadzone_counter += 1
                _motion.move()


            elif _nearest is not None:
                self.deadzone_counter = 0
                print(f"speed : {_nearest.speed}")
                _dir_to_shoot = self.ctrl.get_direction_between(self.my_ship, _nearest)
                print(f"dir_to_shoot: {_dir_to_shoot}")
                _motion.shoot()
                _motion.set_shoot_dir(_dir_to_shoot)

            self.counter += 1
            print(self.counter)
            # objects_in_radius = nm.getObjectsInRadiusOfMe(self.ctrl, self.my_ship, self.radius)
            # asteroids_in_radius = nm.getAsteroidsInRadius(self.ctrl, objects_in_radius)
            # asteroid_resulting_vector = nm.getAsteroidResultingVector(self.ctrl,self.my_ship, asteroids_in_radius)
            # print(asteroid_resulting_vector)
            # _ = nm.moveShipAccordingToVector(self.ctrl, self.my_ship, asteroid_resulting_vector)            
            # if (self.counter > 250): self.counter = 0
            self.ctrl.set_motion_command(_motion)

            




