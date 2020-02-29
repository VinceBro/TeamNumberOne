import numpy as np

class NavigationMethods():
    @staticmethod
    def getObjectsInRadiusOfMe(my_controller, my_ship, radius):
        my_pose = my_ship.xy
        return my_controller.get_mobs_in_radius(my_pose, radius, enemy_only=False)


    @staticmethod
    def getAsteroidsInRadius(my_controller, objects_in_radius):
        all_asteroids = my_controller.get_data_from_asteroids();
        asteroids_in_radius =[]
        for a in all_asteroids:
            if a in objects_in_radius:
                asteroids_in_radius.append(a)

        return asteroids_in_radius

    @staticmethod
    def getAsteroidResultingVector(my_controller, my_ship, asteroids_in_radius):
        weighted_angles = []
        if(len(asteroids_in_radius) > 1):
            for asteroid in asteroids_in_radius:
                u_vector = asteroid.dir
                closest_point = u_vector*asteroid.radius + asteroid.xy
                weight = abs(my_ship.xy-closest_point)
                weighted_angles.append(1/weight * u_vector)

            return sum(weighted_angles)/len(weighted_angles)
        

    @staticmethod
    def moveShipAccordingToVector(my_controller, my_ship, u_vector):
        print(u_vector)
        # angle_direction_to_go = np.angle(u_vector)
        # print(angle_direction_to_go)
    
    @staticmethod
    def getDeadZoneResultingVector(asteroids_in_radius):
        pass
        


    @staticmethod
    def getPlayersResultingVector(players):
        pass
    
    @staticmethod
    def getTotalResultingVector():
        pass

        